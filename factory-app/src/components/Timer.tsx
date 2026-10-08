import { useEffect, useState } from "react"

const SIZE = 36
const CENTER = SIZE / 2
const RADIUS = 12

const colorFor = (remaining: number) => {
  if (remaining > 0.5) return "#22c55e"
  if (remaining > 0.25) return "#facc15"
  return "#ef4444"
}

const Timer = ({ id, timeout }: { id: string; timeout: number }) => {
  const [remaining, setRemaining] = useState(1)

  useEffect(() => {
    if (timeout <= 0) return
    let start = Date.now()
    let frame = 0
    const tick = () => {
      const elapsed = (Date.now() - start) / 1000
      if (elapsed >= timeout) {
        console.log(id)
        start = Date.now()
        setRemaining(1)
      } else {
        setRemaining(1 - elapsed / timeout)
      }
      frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [id, timeout])

  return (
    <svg
      viewBox={`0 0 ${SIZE} ${SIZE}`}
      className="pointer-events-none h-6 w-6"
      aria-hidden="true"
    >
      <circle cx={CENTER} cy={CENTER} r={RADIUS + 3} fill="white" />
      <circle
        cx={CENTER}
        cy={CENTER}
        r={RADIUS}
        fill="none"
        stroke="rgb(0 0 0 / 0.12)"
        strokeWidth="3.5"
      />
      <circle
        cx={CENTER}
        cy={CENTER}
        r={RADIUS}
        fill="none"
        stroke={colorFor(remaining)}
        strokeWidth="3.5"
        strokeLinecap="round"
        pathLength="100"
        strokeDasharray="100"
        strokeDashoffset={(1 - remaining) * 100}
        transform={`rotate(-90 ${CENTER} ${CENTER})`}
      />
    </svg>
  )
}

export default Timer
