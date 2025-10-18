import { Card } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Star } from "lucide-react"

const testimonials = [
  {
    name: "Sarah Mitchell",
    role: "Airbnb Superhost",
    avatar: "/diverse-woman-portrait.png",
    content:
      "ImagiSpaces transformed how I showcase my properties. My booking rate increased by 40% within the first month. The videos are absolutely stunning!",
    rating: 5,
  },
  {
    name: "David Chen",
    role: "Property Manager",
    avatar: "/man.jpg",
    content:
      "Managing 15 properties, I needed a fast solution. ImagiSpaces lets me create professional videos in minutes. My clients love the results.",
    rating: 5,
  },
  {
    name: "Emma Rodriguez",
    role: "Vacation Rental Owner",
    avatar: "/diverse-woman-portrait.png",
    content:
      "The AI does an incredible job capturing the essence of my beach house. Guests always mention the video when they book. Worth every penny!",
    rating: 5,
  },
  {
    name: "Michael Thompson",
    role: "Boutique Hotel Owner",
    avatar: "/man.jpg",
    content:
      "We use ImagiSpaces for all our room listings. The customization options are perfect, and the quality rivals professional videographers.",
    rating: 5,
  },
  {
    name: "Lisa Park",
    role: "Real Estate Agent",
    avatar: "/diverse-woman-portrait.png",
    content:
      "Game changer for my listings! The videos help properties stand out on Booking.com and Vrbo. My clients see results immediately.",
    rating: 5,
  },
  {
    name: "James Wilson",
    role: "Airbnb Host",
    avatar: "/man.jpg",
    content:
      "Simple, fast, and effective. I created my first video in under 10 minutes. The engagement on my listing doubled overnight!",
    rating: 5,
  },
]

export function Testimonials() {
  return (
    <section id="testimonials" className="py-20 sm:py-32">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="mb-4 text-balance text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
            Loved by Property Owners Worldwide
          </h2>
          <p className="text-pretty text-lg text-muted-foreground">
            Join thousands of hosts who are boosting their bookings with AI-powered videos
          </p>
        </div>

        <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {testimonials.map((testimonial, index) => (
            <Card key={index} className="border-border bg-card p-6">
              <div className="mb-4 flex gap-1">
                {Array.from({ length: testimonial.rating }).map((_, i) => (
                  <Star key={i} className="h-4 w-4 fill-accent text-accent" />
                ))}
              </div>
              <p className="mb-6 text-card-foreground">{testimonial.content}</p>
              <div className="flex items-center gap-3">
                <Avatar>
                  <AvatarImage src={testimonial.avatar || "/placeholder.svg"} alt={testimonial.name} />
                  <AvatarFallback>
                    {testimonial.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <div className="font-semibold">{testimonial.name}</div>
                  <div className="text-sm text-muted-foreground">{testimonial.role}</div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
