import SortableSection from "./SortableSection"
import type { Worker } from "../types/worker"

const percentOf = (worker: Worker) => {
  const limit = worker.timeout && worker.timeout > 0 ? worker.timeout : 100
  return Math.min(100, Math.max(0, Math.round((worker.progress / limit) * 100)))
}

const WorkerSection = ({
  type,
  workers,
  onReorder,
}: {
  type: Worker["type"]
  workers: Worker[]
  onReorder: (workers: Worker[]) => void
}) => {
  const title = type.charAt(0).toUpperCase() + type.slice(1)

  return (
    <SortableSection
      title={title}
      sectionId={type}
      items={workers}
      onReorder={onReorder}
      renderItem={(worker) => ({
        title: worker.id.replace(/\D/g, ""),
        caption: worker.status,
        image: worker.image,
        percent: percentOf(worker),
        tone: worker.type,
        timerId: worker.id,
        timeout: worker.timeout,
      })}
    />
  )
}

export default WorkerSection
