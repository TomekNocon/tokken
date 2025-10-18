"use client"

import { Card } from "@/components/ui/card"
import { Sparkles, Zap, Wand2, Video, TrendingUp, Lock } from "lucide-react"
import { useState } from "react"

const features = [
  {
    icon: Wand2,
    title: "AI That Actually Gets It",
    description:
      "Our AI doesn't just stitch photos together. It understands your space, highlights the best angles, and creates a story that sells.",
    color: "from-orange-500 to-red-500",
  },
  {
    icon: Zap,
    title: "Stupid Fast Generation",
    description:
      "Upload. Customize. Download. All in under 5 minutes. Seriously, you'll spend more time choosing the perfect thumbnail.",
    color: "from-yellow-500 to-orange-500",
  },
  {
    icon: Sparkles,
    title: "Your Brand, Your Vibe",
    description:
      "Pick from cinematic styles, add your logo, choose the perfect soundtrack. Make it unmistakably yours.",
    color: "from-purple-500 to-pink-500",
  },
  {
    icon: Video,
    title: "Works Everywhere",
    description:
      "Airbnb, Booking.com, Vrbo, Instagram, TikTok—export in any format. One video, infinite possibilities.",
    color: "from-blue-500 to-cyan-500",
  },
  {
    icon: TrendingUp,
    title: "Bookings Go Brrr",
    description:
      "Listings with videos get 3.5x more clicks and convert like crazy. Your competition is still using photo carousels.",
    color: "from-green-500 to-emerald-500",
  },
  {
    icon: Lock,
    title: "Fort Knox Secure",
    description:
      "Bank-level encryption, GDPR compliant, and your data never trains our AI. Your properties, your privacy.",
    color: "from-slate-500 to-zinc-500",
  },
]

export function Features() {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)

  return (
    <section id="features" className="py-20 sm:py-32 relative">
      <div className="absolute top-1/4 right-0 h-72 w-72 rounded-full bg-accent/10 blur-[100px]" />

      <div className="container relative mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="mb-4 text-balance text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
            Everything You Need,{" "}
            <span className="bg-gradient-to-r from-accent to-[var(--accent-secondary)] bg-clip-text text-transparent">
              Nothing You Don't
            </span>
          </h2>
          <p className="text-pretty text-lg text-muted-foreground">Built for hosts who want results, not complexity</p>
        </div>

        <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <Card
              key={index}
              className="group relative overflow-hidden border-border bg-card p-6 transition-all duration-300 hover:border-accent/50 hover:shadow-2xl hover:shadow-accent/10 hover:-translate-y-1"
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              <div
                className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}
              />

              <div
                className={`relative mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${feature.color} p-[2px] transition-transform duration-300 group-hover:scale-110 group-hover:rotate-3`}
              >
                <div className="flex h-full w-full items-center justify-center rounded-[10px] bg-card">
                  <feature.icon
                    className={`h-5 w-5 bg-gradient-to-br ${feature.color} bg-clip-text text-transparent`}
                  />
                </div>
              </div>

              <h3 className="relative mb-2 text-xl font-semibold">{feature.title}</h3>
              <p className="relative text-muted-foreground leading-relaxed">{feature.description}</p>

              {hoveredIndex === index && (
                <div
                  className={`absolute top-0 right-0 h-20 w-20 bg-gradient-to-br ${feature.color} opacity-10 blur-2xl transition-opacity`}
                />
              )}
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
