import { toast } from "sonner";

export function showError(message, description) {
  toast.error(message || 'Something went wrong', { description });
}

export function showSuccess(message, description) {
  toast.success(message || 'Success', { description });
}

