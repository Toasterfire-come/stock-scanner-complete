import * as React from "react"

import { cn } from "../../lib/utils"
import { Label } from "./label"
import { Input } from "./input"
import { Button } from "./button"

const FormField = ({ label, children, className }) => (
  <div className={cn("space-y-2", className)}>
    {label && <Label>{label}</Label>}
    {children}
  </div>
)

const Form = ({ onSubmit, children, className }) => (
  <form onSubmit={onSubmit} className={cn("space-y-4", className)}>
    {children}
  </form>
)

export { Form, FormField, Label, Input, Button }
