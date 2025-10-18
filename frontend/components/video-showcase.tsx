"use client"

import { Card } from "@/components/ui/card"
import { Play } from "lucide-react"
import { useState } from "react"

const showcaseVideos = [
  {
    title: "Beachfront Villa",
    location: "Malibu, CA",
    thumbnail: "/luxury-beachfront-villa-sunset-ocean-view.jpg",
    stats: "+245% bookings",
  },
  {
    title: "Mountain Cabin",
    location: "Aspen, CO",
    thumbnail: "/cozy-mountain-cabin-snow-forest.jpg",
    stats: "+180% engagement",
  },
  {
    title: "Urban Loft",
    location: "Brooklyn, NY",
    thumbnail: "/modern-urban-loft-industrial-design.jpg",
    stats: "+320% views",
  },
]

export function VideoShowcase() {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)

  return (
    <section className="py-20 sm:py-32 bg-muted/30">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="mb-4 text-balance text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
            See the{" "}
            <span className="bg-gradient-to-r from-accent to-[var(--accent-secondary)] bg-clip-text text-transparent">
              Transformation
            </span>
          </h2>
          <p className="text-pretty text-lg text-muted-foreground">
            Real properties, real results. Watch how AI turns ordinary listings into extraordinary experiences.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {showcaseVideos.map((video, index) => (
            <Card
              key={index}
              className="group relative overflow-hidden border-border bg-card transition-all duration-300 hover:border-accent/50 hover:shadow-2xl hover:shadow-accent/10"
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              <div className="relative aspect-video overflow-hidden">
                <img
                  src={video.thumbnail || "/placeholder.svg"}
                  alt={video.title}
                  className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />

                {/* Play button overlay */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <div
                    className={`flex h-16 w-16 items-center justify-center rounded-full bg-accent/90 backdrop-blur-sm transition-all duration-300 ${hoveredIndex === index ? "scale-110" : "scale-100"}`}
                  >
                    <Play className="h-6 w-6 fill-accent-foreground text-accent-foreground ml-1" />
                  </div>
                </div>

                {/* Stats badge */}
                <div className="absolute top-4 right-4 rounded-full bg-accent/90 backdrop-blur-sm px-3 py-1 text-xs font-semibold text-accent-foreground">
                  {video.stats}
                </div>
              </div>

              <div className="p-4">
                <h3 className="text-lg font-semibold mb-1">{video.title}</h3>
                <p className="text-sm text-muted-foreground">{video.location}</p>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
