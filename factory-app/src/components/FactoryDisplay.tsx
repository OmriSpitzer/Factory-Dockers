import { useEffect, useRef, useState } from "react"
import type { Client } from "../types/client"
import type { Worker } from "../types/worker"
import SortableSection from "./SortableSection"
import WorkerSection from "./WorkerSection"

const orderByIds = <T extends { id: string }>(ids: string[], incoming: T[]) => {
  const byId = new Map(incoming.map((item) => [item.id, item]))
  const kept = ids.flatMap((id) => {
    const item = byId.get(id)
    return item ? [item] : []
  })
  const keptIds = new Set(kept.map((item) => item.id))
  return [...kept, ...incoming.filter((item) => !keptIds.has(item.id))]
}


const groupByType = (workers: Worker[]) => {
  const grouped: Record<string, Worker[]> = {}
  for (const worker of workers) {
    grouped[worker.type] ??= []
    grouped[worker.type].push(worker)
  }
  return grouped
}

const sectionOrder = ["assembler", "tester", "packager", "shipper"] as const

const FactoryDisplay = ({
  clients,
  onClients,
}: {
  clients: Client[]
  onClients: (clients: Client[]) => void
}) => {
  const [mappedWorkers, setMappedWorkers] = useState<Record<string, Worker[]>>({})
  const workerOrder = useRef<Record<string, string[]>>({})
  const clientOrder = useRef<string[]>([])

  useEffect(() => {
    let cancelled = false
    let socket: WebSocket | null = null
    let retry: ReturnType<typeof setTimeout> | undefined

    const applyWorkers = (records: { id: string; worker: Worker }[]) => {
      const grouped = groupByType(records.map((record) => ({ ...record.worker, id: record.id })))
      const next: Record<string, Worker[]> = {}
      for (const type of Object.keys(grouped)) {
        const ordered = orderByIds(workerOrder.current[type] ?? [], grouped[type])
        workerOrder.current[type] = ordered.map((worker) => worker.id)
        next[type] = ordered
      }
      setMappedWorkers(next)
    }

    const loadWorkers = () => {
      fetch("/api/worker")
        .then((response) => {
          if (!response.ok) throw new Error("worker request failed")
          return response.json()
        })
        .then((records: { id: string; worker: Worker }[]) => {
          if (!cancelled) applyWorkers(records)
        })
        .catch(() => {})
    }

    const loadClients = () => {
      fetch("/api/client")
        .then((response) => {
          if (!response.ok) throw new Error("client request failed")
          return response.json()
        })
        .then((records: Client[]) => {
          if (cancelled) return
          const ordered = orderByIds(clientOrder.current, records)
          clientOrder.current = ordered.map((client) => client.id)
          onClients(ordered)
        })
        .catch(() => {})
    }

    const connect = () => {
      if (cancelled) return
      const protocol = location.protocol === "https:" ? "wss" : "ws"
      socket = new WebSocket(`${protocol}://${location.host}/api/subscribe`)
      socket.onmessage = (event) => {
        if (cancelled) return
        const payload = JSON.parse(event.data) as {
          clients?: Client[]
          workers?: { id: string; worker: Worker }[]
        }
        if (payload.clients) {
          const ordered = orderByIds(clientOrder.current, payload.clients)
          clientOrder.current = ordered.map((client) => client.id)
          onClients(ordered)
        }
        if (payload.workers) applyWorkers(payload.workers)
      }
      socket.onclose = () => {
        if (cancelled) return
        retry = setTimeout(connect, 1000)
      }
    }

    loadWorkers()
    loadClients()
    connect()

    return () => {
      cancelled = true
      clearTimeout(retry)
      socket?.close()
    }
  }, [onClients]);

  return (
    <div className="grid h-full w-full grid-cols-5 gap-4 p-4">
      <SortableSection
        title="Clients"
        sectionId="clients"
        items={clients}
        onReorder={(next) => {
          clientOrder.current = next.map((client) => client.id)
          onClients(next)
        }}
        renderItem={(client) => ({
          title: client.name,
          caption: `${client.timeout}s`,
          image: client.image,
          tone: "client",
        })}
      />
      {sectionOrder.map((type) => (
        <WorkerSection
          key={type}
          type={type}
          workers={mappedWorkers[type] ?? []}
          onReorder={(next) => {
            workerOrder.current[type] = next.map((worker) => worker.id)
            setMappedWorkers((current) => ({ ...current, [type]: next }))
          }}
        />
      ))}
    </div>
  )
}

export default FactoryDisplay
