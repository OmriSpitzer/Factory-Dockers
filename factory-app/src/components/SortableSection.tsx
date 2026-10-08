import { useLayoutEffect, useRef, useState } from "react"
import type { PointerEvent as ReactPointerEvent } from "react"
import Card from "./Card"

type CardFields = {
  title: string
  caption?: string
  image?: string
  percent?: number
  tone: "client" | "assembler" | "tester" | "packager" | "shipper"
  timerId?: string
  timeout?: number
}

type Point = {
  x: number
  y: number
}

type Drag = {
  id: string
  from: number
  over: number
  slot: number
  dy: number
}

const BOTTOM_PAD = 16

const clamp = (value: number, min: number, max: number) => Math.min(Math.max(value, min), max)

const moveItem = <T,>(items: T[], from: number, to: number) => {
  const next = items.slice()
  const [item] = next.splice(from, 1)
  next.splice(to, 0, item)
  return next
}

const shiftFor = (index: number, from: number, over: number, slot: number) => {
  if (index === from) return 0
  if (from < over && index > from && index <= over) return -slot
  if (over < from && index >= over && index < from) return slot
  return 0
}

const SortableSection = <T extends { id: string }>({
  title,
  sectionId,
  items,
  onReorder,
  renderItem,
}: {
  title: string
  sectionId: string
  items: T[]
  onReorder: (items: T[]) => void
  renderItem: (item: T) => CardFields
}) => {
  const itemsRef = useRef(items)
  itemsRef.current = items
  const listRef = useRef<HTMLElement>(null)
  const flipFrom = useRef<Map<string, Point> | null>(null)
  const dragRef = useRef<Drag | null>(null)
  const [drag, setDrag] = useState<Drag | null>(null)
  const [settle, setSettle] = useState(0)

  useLayoutEffect(() => {
    const previous = flipFrom.current
    const list = listRef.current
    if (!previous || !list) return
    flipFrom.current = null
    const animated: HTMLElement[] = []
    list.querySelectorAll<HTMLElement>("[data-card-visual]").forEach((node) => {
      const id = node.dataset.cardId
      const from = id ? previous.get(id) : undefined
      if (!from) return
      const box = node.getBoundingClientRect()
      const dx = from.x - box.left
      const dy = from.y - box.top
      if (Math.abs(dx) < 0.5 && Math.abs(dy) < 0.5) return
      node.style.transition = "none"
      node.style.transform = `translate(${dx}px, ${dy}px)`
      animated.push(node)
    })
    if (animated.length === 0) return
    animated[0].getBoundingClientRect()
    requestAnimationFrame(() => {
      animated.forEach((node) => {
        node.style.transition = "transform 240ms cubic-bezier(0.22, 1, 0.36, 1)"
        node.style.transform = "translate(0px, 0px)"
        node.addEventListener(
          "transitionend",
          () => {
            node.style.transition = ""
            node.style.transform = ""
          },
          { once: true },
        )
      })
    })
  }, [items, settle])

  const updateDrag = (next: Drag | null) => {
    dragRef.current = next
    setDrag(next)
  }

  const onPointerDown = (id: string) => (event: ReactPointerEvent<HTMLDivElement>) => {
    if (event.button !== 0) return
    const list = listRef.current
    if (!list) return
    list.querySelectorAll<HTMLElement>("[data-card-visual]").forEach((node) => {
      node.style.transition = ""
      node.style.transform = ""
    })
    const visual = event.currentTarget
    const rect = visual.getBoundingClientRect()
    const slotNode = visual.parentElement
    if (!slotNode) return
    const nextRect = (slotNode.nextElementSibling as HTMLElement | null)?.getBoundingClientRect()
    const slot = nextRect ? nextRect.top - slotNode.getBoundingClientRect().top : rect.height + 12
    const originY = event.clientY
    const slots = [...list.querySelectorAll<HTMLElement>("[data-slot]")]
    const mids = slots.map((node) => {
      const box = node.getBoundingClientRect()
      return box.top + box.height / 2
    })

    let grabbing = false
    const move = (pointer: PointerEvent) => {
      if (!dragRef.current && Math.abs(pointer.clientY - originY) < 5) return
      const cards = itemsRef.current
      const from = cards.findIndex((item) => item.id === id)
      if (from < 0 || slot <= 0) return
      let over = 0
      mids.forEach((mid, index) => {
        if (pointer.clientY >= mid) over = index
      })
      const sectionBox = list.getBoundingClientRect()
      const headerBottom = document.querySelector("header")?.getBoundingClientRect().bottom ?? 0
      const limitTop = Math.max(sectionBox.top, headerBottom)
      const limitBottom = Math.min(sectionBox.bottom, window.innerHeight - BOTTOM_PAD)
      let applied = clamp(over, 0, cards.length - 1) - from
      while (applied > 0 && rect.top + applied * slot + rect.height > limitBottom) applied -= 1
      while (applied < 0 && rect.top + applied * slot < limitTop) applied += 1
      const dy = clamp(pointer.clientY - originY, limitTop - rect.top, limitBottom - rect.bottom)
      if (!grabbing) {
        grabbing = true
        document.body.style.cursor = "grabbing"
      }
      updateDrag({ id, from, over: from + applied, slot, dy })
    }

    const up = () => {
      window.removeEventListener("pointermove", move)
      window.removeEventListener("pointerup", up)
      window.removeEventListener("pointercancel", up)
      if (grabbing) document.body.style.cursor = ""
      const current = dragRef.current
      if (current) {
        const places = new Map<string, Point>()
        list.querySelectorAll<HTMLElement>("[data-card-visual]").forEach((node) => {
          const cardId = node.dataset.cardId
          if (!cardId) return
          const box = node.getBoundingClientRect()
          places.set(cardId, { x: box.left, y: box.top })
        })
        flipFrom.current = places
        setSettle((value) => value + 1)
      }
      updateDrag(null)
      if (!current || current.over === current.from) return
      const cards = itemsRef.current
      const from = cards.findIndex((item) => item.id === current.id)
      if (from < 0) return
      const to = clamp(current.over, 0, cards.length - 1)
      if (from === to) return
      onReorder(moveItem(cards, from, to))
    }

    window.addEventListener("pointermove", move)
    window.addEventListener("pointerup", up)
    window.addEventListener("pointercancel", up)
  }

  return (
    <section
      ref={listRef}
      data-section={sectionId}
      className="relative flex h-full min-h-0 flex-col gap-3 overflow-x-hidden overflow-y-auto rounded-2xl bg-section p-4"
    >
      <h2 className="text-sm font-semibold tracking-tight text-text-h">{title}</h2>
      {items.map((item, index) => {
        const fields = renderItem(item)
        const isDragged = drag?.id === item.id
        const shift = drag
          ? isDragged
            ? (drag.over - drag.from) * drag.slot
            : shiftFor(index, drag.from, drag.over, drag.slot)
          : 0

        return (
          <div
            key={item.id}
            data-slot={item.id}
            className="flex touch-none justify-center select-none"
          >
            <div
              data-card-id={item.id}
              data-card-visual=""
              onPointerDown={onPointerDown(item.id)}
              className={`w-[68%] max-w-36 ${drag ? "cursor-grabbing" : "cursor-grab"}`}
              style={
                isDragged && drag
                  ? {
                      position: "relative",
                      zIndex: 5,
                      transform: `translateY(${drag.dy}px) scale(1.03)`,
                      transition: "none",
                    }
                  : shift === 0
                    ? undefined
                    : {
                        position: "relative",
                        zIndex: 1,
                        transform: `translateY(${shift}px)`,
                        transition: "transform 220ms cubic-bezier(0.22, 1, 0.36, 1)",
                      }
              }
            >
              <Card {...fields} lifted={isDragged} />
            </div>
          </div>
        )
      })}
    </section>
  )
}

export default SortableSection
