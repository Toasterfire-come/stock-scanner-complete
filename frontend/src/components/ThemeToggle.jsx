import React from "react";
import { Moon, Sun } from "lucide-react";
import { Button } from "./ui/button";

function applyThemeClass(isDark) {
  try {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  } catch {}
}

function getInitialPreference() {
  try {
    const saved = localStorage.getItem('tsp_theme');
    if (saved === 'dark') return true;
    if (saved === 'light') return false;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  } catch {
    return false;
  }
}

const ThemeToggle = () => {
  const [isDark, setIsDark] = React.useState(getInitialPreference());

  React.useEffect(() => {
    applyThemeClass(isDark);
    try { localStorage.setItem('tsp_theme', isDark ? 'dark' : 'light'); } catch {}
  }, [isDark]);

  React.useEffect(() => {
    try {
      const mql = window.matchMedia('(prefers-color-scheme: dark)');
      const handler = (e) => {
        const saved = localStorage.getItem('tsp_theme');
        if (!saved) {
          setIsDark(Boolean(e.matches));
        }
      };
      mql.addEventListener('change', handler);
      return () => mql.removeEventListener('change', handler);
    } catch {}
  }, []);

  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      onClick={() => setIsDark((v) => !v)}
      className="h-9 w-9 rounded-md"
    >
      <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  );
};

export default ThemeToggle;

