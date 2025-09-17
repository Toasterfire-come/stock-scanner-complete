import React from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "./ui/dialog";

export default function ShortcutsHelp({ open, onOpenChange }) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent aria-label="Keyboard Shortcuts">
        <DialogHeader>
          <DialogTitle>Keyboard Shortcuts</DialogTitle>
          <DialogDescription>Work faster with these built-in shortcuts</DialogDescription>
        </DialogHeader>
        <div className="grid sm:grid-cols-2 gap-4 text-sm">
          <div className="rounded border p-3">
            <div className="font-medium mb-1">Open Search</div>
            <div className="text-muted-foreground">Ctrl + K (Cmd + K on Mac)</div>
          </div>
          <div className="rounded border p-3">
            <div className="font-medium mb-1">Help Overlay</div>
            <div className="text-muted-foreground">?</div>
          </div>
          <div className="rounded border p-3">
            <div className="font-medium mb-1">Navigate Results</div>
            <div className="text-muted-foreground">Up / Down</div>
          </div>
          <div className="rounded border p-3">
            <div className="font-medium mb-1">Select Item</div>
            <div className="text-muted-foreground">Enter</div>
          </div>
          <div className="rounded border p-3">
            <div className="font-medium mb-1">Close Dialog</div>
            <div className="text-muted-foreground">Esc</div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

