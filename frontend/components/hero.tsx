"use client"

import { Button } from "@/components/ui/button"
import { ArrowRight, Play, Sparkles } from "lucide-react"
import { useState } from "react"

export function Hero() {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <section className="relative overflow-hidden pt-32 pb-20 sm:pt-40 sm:pb-32">
      <div className="absolute top-20 left-1/4 h-96 w-96 rounded-full bg-accent/20 blur-[120px] animate-float" />
      <div
        className="absolute bottom-20 right-1/4 h-96 w-96 rounded-full bg-[var(--accent-secondary)]/20 blur-[120px] animate-float"
        style={{ animationDelay: "2s" }}
      />

      <div className="container relative mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-5xl text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-accent/30 bg-accent/5 px-4 py-1.5 text-sm backdrop-blur-sm">
            <Sparkles className="h-3.5 w-3.5 text-accent animate-pulse" />
            <span className="bg-gradient-to-r from-accent to-[var(--accent-secondary)] bg-clip-text text-transparent font-medium">
              AI-Powered Video Magic
            </span>
          </div>

          <h1 className="mb-6 text-balance text-5xl font-bold tracking-tight sm:text-6xl lg:text-7xl">
            Turn Static Photos Into{" "}
            <span className="relative inline-block">
              <span className="bg-gradient-to-r from-accent via-[var(--accent-secondary)] to-accent bg-clip-text text-transparent animate-glow">
                Cinematic Experiences
              </span>
              <svg
                className="absolute -bottom-2 left-0 w-full"
                height="8"
                viewBox="0 0 300 8"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M1 5.5C50 2.5 100 1 150 2.5C200 4 250 5.5 299 3"
                  stroke="currentColor"
                  strokeWidth="3"
                  strokeLinecap="round"
                  className="text-accent"
                />
              </svg>
            </span>
          </h1>

          <p className="mx-auto mb-10 max-w-2xl text-pretty text-lg text-muted-foreground sm:text-xl leading-relaxed">
            Your properties deserve more than boring photo galleries. Create scroll-stopping AI videos that make guests
            say "wow" and hit that book button faster than you can say "5-star review."
          </p>

          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button
              size="lg"
              className="group relative overflow-hidden bg-accent hover:bg-accent/90 text-accent-foreground shadow-lg shadow-accent/25"
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
            >
              <span className="relative z-10 flex items-center">
                Create Your First Video Free
                <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
              </span>
              {isHovered && (
                <span className="absolute inset-0 bg-gradient-to-r from-accent to-[var(--accent-secondary)] animate-pulse" />
              )}
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="group border-accent/30 bg-transparent hover:bg-accent/5 hover:border-accent"
            >
              <Play className="mr-2 h-4 w-4 fill-accent text-accent" />
              See the Magic in Action
            </Button>
          </div>

          <div className="mt-16 flex flex-wrap items-center justify-center gap-x-12 gap-y-6">
            <div className="group relative">
              <div className="absolute inset-0 bg-accent/10 blur-xl rounded-full group-hover:bg-accent/20 transition-colors" />
              <div className="relative flex flex-col items-center">
                <span className="text-3xl font-bold bg-gradient-to-br from-accent to-[var(--accent-secondary)] bg-clip-text text-transparent">
                  10K+
                </span>
                <span className="text-sm text-muted-foreground">Videos Created</span>
              </div>
            </div>
            <div className="group relative">
              <div className="absolute inset-0 bg-accent/10 blur-xl rounded-full group-hover:bg-accent/20 transition-colors" />
              <div className="relative flex flex-col items-center">
                <span className="text-3xl font-bold bg-gradient-to-br from-accent to-[var(--accent-secondary)] bg-clip-text text-transparent">
                  3.5x
                </span>
                <span className="text-sm text-muted-foreground">More Bookings</span>
              </div>
            </div>
            <div className="group relative">
              <div className="absolute inset-0 bg-accent/10 blur-xl rounded-full group-hover:bg-accent/20 transition-colors" />
              <div className="relative flex flex-col items-center">
                <span className="text-3xl font-bold bg-gradient-to-br from-accent to-[var(--accent-secondary)] bg-clip-text text-transparent">
                  &lt;5min
                </span>
                <span className="text-sm text-muted-foreground">To Create</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(var(--accent)/0.05),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,rgba(var(--accent-secondary)/0.05),transparent_50%)]" />
      </div>
    </section>
  )
}
