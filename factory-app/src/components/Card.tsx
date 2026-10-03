const cardBackground = {
  client: "bg-client",
  assembler: "bg-assembler",
  tester: "bg-tester",
  packager: "bg-packager",
  shipper: "bg-shipper",
} as const

type CardTone = keyof typeof cardBackground

const Card = ({
  title,
  caption,
  image,
  percent,
  tone,
  lifted = false,
}: {
  title: string
  caption?: string
  image?: string
  percent?: number
  tone: CardTone
  lifted?: boolean
}) => {
  return (
    <article
      className={`flex w-full flex-col items-center gap-2 rounded-2xl px-3 py-3 text-card-text ring-1 ring-border ${cardBackground[tone]} ${
        lifted ? "shadow-md" : "shadow-sm"
      }`}
    >
      {image ? (
        <img
          src={image}
          alt=""
          draggable={false}
          className="pointer-events-none h-14 w-14 rounded-xl bg-white object-cover ring-2 ring-white"
        />
      ) : null}
      <p className="text-center text-xs font-semibold tracking-[0.08em]">{title}</p>
      {caption ? (
        <p className="text-[10px] font-medium uppercase tracking-[0.16em]">{caption}</p>
      ) : null}
      {percent !== undefined ? (
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-bar-track">
          <div className="h-full rounded-full bg-bar" style={{ width: `${percent}%` }} />
        </div>
      ) : null}
    </article>
  )
}

export default Card
