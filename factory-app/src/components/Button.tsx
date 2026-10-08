import type { ButtonHTMLAttributes } from "react"

const variantClass = {
  primary: "bg-[#16a34a] text-white hover:bg-[#15803d]",
  danger: "bg-[#dc2626] text-white hover:bg-[#b91c1c]",
  neutral: "border border-border bg-code-bg text-text-h hover:bg-border",
} as const

const sizeClass = {
  md: "px-5 py-2 text-base",
  sm: "px-3.5 py-1.5 text-sm",
} as const

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: keyof typeof variantClass
  size?: keyof typeof sizeClass
}

/**
 * Shared button for actions across the app.
 */
const Button = ({variant = "primary",size = "md",type = "button",className = "",...props}: ButtonProps) => {
  return (
    <button
      type={type}
      className={`rounded-full font-medium shadow-sm transition duration-150 hover:-translate-y-0.5 hover:shadow-md disabled:pointer-events-none disabled:opacity-50 ${variantClass[variant]} ${sizeClass[size]} ${className}`}
      {...props}
    />
  )
}

export default Button
