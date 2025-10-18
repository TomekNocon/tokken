import { Card } from "@/components/ui/card"
import { Upload, Wand2, Download } from "lucide-react"

const steps = [
  {
    icon: Upload,
    step: "01",
    title: "Upload Your Photos",
    description:
      "Simply drag and drop your property photos. We support all major image formats and recommend 10-20 photos for best results.",
  },
  {
    icon: Wand2,
    step: "02",
    title: "Customize & Generate",
    description:
      "Choose your video style, music, and add custom text. Our AI analyzes your photos and creates a cinematic tour in minutes.",
  },
  {
    icon: Download,
    step: "03",
    title: "Download & Share",
    description:
      "Preview your video, make any final adjustments, then download in your preferred format. Ready to upload to any platform.",
  },
]

export function HowItWorks() {
  return (
    <section id="how-it-works" className="bg-muted/30 py-20 sm:py-32">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="mb-4 text-balance text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
            Create Your Video in 3 Simple Steps
          </h2>
          <p className="text-pretty text-lg text-muted-foreground">From photos to professional video in minutes</p>
        </div>

        <div className="mt-16 grid gap-8 lg:grid-cols-3">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              <Card className="h-full border-border bg-card p-8">
                <div className="mb-6 flex items-center justify-between">
                  <div className="inline-flex h-16 w-16 items-center justify-center rounded-xl bg-accent/10 text-accent">
                    <step.icon className="h-8 w-8" />
                  </div>
                  <span className="text-6xl font-bold text-muted/20">{step.step}</span>
                </div>
                <h3 className="mb-3 text-2xl font-semibold">{step.title}</h3>
                <p className="text-muted-foreground">{step.description}</p>
              </Card>
              {index < steps.length - 1 && (
                <div className="absolute right-0 top-1/2 hidden h-0.5 w-8 -translate-y-1/2 translate-x-full bg-border lg:block" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
