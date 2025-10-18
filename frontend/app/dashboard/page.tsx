"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import {
  Upload,
  GripVertical,
  Home,
  Building2,
  Castle,
  Bed,
  ChevronDown,
  Sparkles,
  Briefcase,
  TrendingUp,
  Play,
  Download,
  Share2,
  RotateCcw,
  X,
} from "lucide-react"
import { ThemeToggle } from "@/components/theme-toggle"

type PropertyType = "house" | "apartment" | "villa" | "studio"
type Platform = "airbnb" | "instagram" | "tiktok" | "facebook" | "email" | "mls"
type Vibe = "luxury" | "fun" | "business" | "family"
type ColorMood = "warm" | "cool" | "natural" | "vibrant"
type GenerationStep = "analyzing" | "styling" | "transitions" | "finalizing" | "complete"

interface Character {
  id: string
  name: string
  image_paths: string[]
  generated_path: string
  health: number
  wins: number
  losses: number
  created_at: string
  status: string
}

const API_BASE_URL = "http://127.0.0.1:8000"

export default function DashboardPage() {
  const [photos, setPhotos] = useState<File[]>([])
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null)
  const [propertyName, setPropertyName] = useState("")
  const [propertyType, setPropertyType] = useState<PropertyType>("house")
  const [selectedPlatform, setSelectedPlatform] = useState<Platform | null>(null)
  const [selectedVibe, setSelectedVibe] = useState<Vibe | null>(null)
  const [advancedOpen, setAdvancedOpen] = useState(false)
  const [openingText, setOpeningText] = useState("")
  const [colorMood, setColorMood] = useState<ColorMood>("natural")
  const [transitionSpeed, setTransitionSpeed] = useState([50])
  const [musicMood, setMusicMood] = useState("none")
  const [ctaText, setCtaText] = useState("")
  const [createABTest, setCreateABTest] = useState(false)
  const [addToSchedule, setAddToSchedule] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationStep, setGenerationStep] = useState<GenerationStep>("analyzing")
  const [progress, setProgress] = useState(0)
  const [videoGenerated, setVideoGenerated] = useState(false)
  const [generatedCharacter, setGeneratedCharacter] = useState<Character | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [showAddYourself, setShowAddYourself] = useState(false)
  const [userPhoto, setUserPhoto] = useState<File | null>(null)
  const [isCombiningImages, setIsCombiningImages] = useState(false)
  const [combinedImageUrl, setCombinedImageUrl] = useState<string | null>(null)

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const files = Array.from(e.dataTransfer.files).filter((file) => file.type.startsWith("image/"))
    setPhotos(files.slice(0, 3))
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files).filter((file) => file.type.startsWith("image/"))
      setPhotos(files.slice(0, 3))
    }
  }

  const handleRemovePhoto = (index: number) => {
    setPhotos((prev) => prev.filter((_, i) => i !== index))
  }

  const handleDragStart = (index: number) => {
    setDraggedIndex(index)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  const handleDropReorder = (dropIndex: number) => {
    if (draggedIndex === null || draggedIndex === dropIndex) return

    const newPhotos = [...photos]
    const draggedPhoto = newPhotos[draggedIndex]
    newPhotos.splice(draggedIndex, 1)
    newPhotos.splice(dropIndex, 0, draggedPhoto)

    setPhotos(newPhotos)
    setDraggedIndex(null)
  }

  const handleUserPhotoSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setUserPhoto(e.target.files[0])
    }
  }

  const handleCombineImages = async () => {
    if (!userPhoto || photos.length === 0) {
      setError("Please upload your photo and at least one property image")
      return
    }

    setIsCombiningImages(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append("background_image", photos[0]) // Use first photo as background
      formData.append("person_image", userPhoto)
      formData.append("prompt", "Person naturally placed in this room environment, realistic lighting, seamless integration")

      const response = await fetch(`${API_BASE_URL}/combine-images/`, {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Unknown error" }))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      setCombinedImageUrl(result.combined_image_url)
      setShowAddYourself(false)
      
    } catch (err) {
      console.error("Error combining images:", err)
      setError(err instanceof Error ? err.message : "Failed to combine images")
    } finally {
      setIsCombiningImages(false)
    }
  }

  const handleGenerate = async () => {
    if (photos.length === 0 || !propertyName) {
      setError("Please upload photos and enter a property name")
      return
    }

    setIsGenerating(true)
    setProgress(0)
    setGenerationStep("analyzing")
    setError(null)

    try {
      // Create FormData for file upload
      const formData = new FormData()
      
      // Add original photos
      photos.forEach((photo) => {
        formData.append("images", photo)
      })
      
      // If there's a combined image, fetch it and add it as the third image
      if (combinedImageUrl) {
        try {
          const combinedResponse = await fetch(`${API_BASE_URL}${combinedImageUrl}`)
          const combinedBlob = await combinedResponse.blob()
          const combinedFile = new File([combinedBlob], "combined_image.png", { type: "image/png" })
          formData.append("images", combinedFile)
        } catch (err) {
          console.error("Error adding combined image:", err)
          // Continue without the combined image
        }
      }
      
      formData.append("name", propertyName)
      
      // Add optional prompt based on selected vibe and platform
      let customPrompt = "create a virtual tour video of this property"
      if (selectedVibe) {
        switch (selectedVibe) {
          case "luxury":
            customPrompt = "create an elegant, slow-paced luxury property tour video"
            break
          case "fun":
            customPrompt = "create an upbeat, energetic property tour video"
            break
          case "business":
            customPrompt = "create a professional business-focused property tour video"
            break
          case "family":
            customPrompt = "create a warm, family-friendly property tour video"
            break
        }
      }
      if (openingText) {
        customPrompt += ` with opening text: "${openingText}"`
      }
      formData.append("prompt", customPrompt)

      // Simulate progress steps
      const steps: GenerationStep[] = ["analyzing", "styling", "transitions", "finalizing"]
      let currentStep = 0
      
      const progressInterval = setInterval(() => {
        if (currentStep < steps.length) {
          setGenerationStep(steps[currentStep])
          setProgress((currentStep / steps.length) * 80) // Leave 20% for final processing
          currentStep++
        }
      }, 1000)

      // Make API call to create character
      const response = await fetch(`${API_BASE_URL}/characters/`, {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Unknown error" }))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      
      // Get the created character details
      const characterResponse = await fetch(`${API_BASE_URL}/characters/${result.character_id}`)
      if (!characterResponse.ok) {
        throw new Error("Failed to get character details")
      }
      
      const character = await characterResponse.json()
      
      clearInterval(progressInterval)
      setProgress(100)
      setGenerationStep("complete")
      setGeneratedCharacter(character)
      setIsGenerating(false)
      setVideoGenerated(true)

    } catch (err) {
      console.error("Error generating character:", err)
      setError(err instanceof Error ? err.message : "Failed to generate video")
      setIsGenerating(false)
      setProgress(0)
    }
  }

  const platforms = [
    { id: "airbnb", name: "Airbnb", desc: "Professional showcase", icon: "🏠" },
    { id: "instagram", name: "Instagram Reel", desc: "Trendy & vertical", icon: "📸" },
    { id: "tiktok", name: "TikTok", desc: "Short & engaging", icon: "🎵" },
    { id: "facebook", name: "Facebook", desc: "Wide reach", icon: "👥" },
    { id: "email", name: "Email/Newsletter", desc: "Direct marketing", icon: "✉️" },
    { id: "mls", name: "MLS Listing", desc: "Professional standard", icon: "🏢" },
  ]

  const vibes = [
    { id: "luxury", name: "Luxury Escape", desc: "Slow, elegant" },
    { id: "fun", name: "Fun Getaway", desc: "Upbeat, energetic" },
    { id: "business", name: "Business Ready", desc: "Workspace focus" },
    { id: "family", name: "Family Friendly", desc: "Spacious & safe" },
  ]

  const propertyTypes = [
    { id: "house", name: "House", icon: Home },
    { id: "apartment", name: "Apartment", icon: Building2 },
    { id: "villa", name: "Villa", icon: Castle },
    { id: "studio", name: "Studio", icon: Bed },
  ]

  const smartSuggestions = [
    { icon: Sparkles, text: "Pool detected - featuring prominently" },
    { icon: Briefcase, text: "Workspace visible - great for business travelers" },
  ]

  const getStepText = () => {
    switch (generationStep) {
      case "analyzing":
        return "Analyzing photos..."
      case "styling":
        return "Applying style..."
      case "transitions":
        return "Adding transitions..."
      case "finalizing":
        return "Finalizing..."
      case "complete":
        return "Complete!"
      default:
        return ""
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="relative border-b border-border backdrop-blur-sm bg-background/80">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-accent to-orange-500 rounded-lg" />
            <span className="text-xl font-bold">ImagiSpaces</span>
          </div>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <Button variant="ghost" size="sm">
              My Videos
            </Button>
          </div>
        </div>
      </header>

      <div className="relative container mx-auto px-4 py-8">
        {/* Competitive Intelligence Box */}
        <Card className="mb-6 bg-accent/5 border-accent/20 p-4">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-5 h-5 text-accent" />
            <p className="text-sm">
              <span className="font-semibold">Properties with video get 40% more bookings</span>
              <span className="text-muted-foreground"> • You'll be in the top 12%</span>
            </p>
          </div>
        </Card>

        <div className="grid lg:grid-cols-[40%_60%] gap-8">
          {/* Left Column */}
          <div className="space-y-6">
            {/* Drag and Drop Zone */}
            <Card className="bg-card border-border p-6">
              <Label className="text-sm font-medium mb-3 block">Upload Photos</Label>
              <div
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                className="border-2 border-dashed border-border rounded-lg p-12 text-center hover:border-accent/50 transition-colors cursor-pointer group"
                onClick={() => document.getElementById("file-input")?.click()}
              >
                <Upload className="w-12 h-12 mx-auto mb-4 text-muted-foreground group-hover:text-accent transition-colors" />
                <p className="text-muted-foreground mb-1">
                  {photos.length > 0 ? "Click to replace photos" : "Drag 3 photos here or click to browse"}
                </p>
                <p className="text-sm text-muted-foreground">{photos.length}/3 photos uploaded</p>
                <input
                  id="file-input"
                  type="file"
                  multiple
                  accept="image/*"
                  className="hidden"
                  onChange={handleFileSelect}
                />
              </div>

              {/* Photo Preview Slots */}
              {photos.length > 0 && (
                <div className="mt-6 space-y-3">
                  {["Opening Shot", "Main Feature", "Closing Shot"].map((label, idx) => (
                    <div
                      key={label}
                      draggable={!!photos[idx]}
                      onDragStart={() => handleDragStart(idx)}
                      onDragOver={handleDragOver}
                      onDrop={() => handleDropReorder(idx)}
                      className={`flex items-center gap-3 p-3 bg-muted/50 rounded-lg border border-border transition-all ${
                        photos[idx] ? "cursor-move hover:bg-muted" : ""
                      } ${draggedIndex === idx ? "opacity-50" : ""}`}
                    >
                      <GripVertical className="w-4 h-4 text-muted-foreground" />
                      <div className="w-16 h-16 bg-muted rounded overflow-hidden">
                        {photos[idx] && (
                          <img
                            src={URL.createObjectURL(photos[idx]) || "/placeholder.svg"}
                            alt={label}
                            className="w-full h-full object-cover"
                          />
                        )}
                      </div>
                      <span className="text-sm text-muted-foreground flex-1">{label}</span>
                      {photos[idx] && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleRemovePhoto(idx)
                          }}
                          className="p-1 rounded-full hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-colors"
                          aria-label="Remove photo"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Add Yourself Button */}
              {photos.length > 0 && (
                <div className="mt-4">
                  <Button
                    variant="outline"
                    onClick={() => setShowAddYourself(true)}
                    className="w-full border-dashed border-accent/50 text-accent hover:bg-accent/10"
                  >
                    <Upload className="w-4 h-4 mr-2" />
                    Add Yourself to the Scene
                  </Button>
                  {combinedImageUrl && (
                    <div className="mt-2 p-2 bg-accent/10 rounded-lg text-sm text-accent">
                      ✓ You've been added to the first image
                    </div>
                  )}
                </div>
              )}
            </Card>

            {/* Property Details */}
            <Card className="bg-card border-border p-6 space-y-4">
              <div>
                <Label htmlFor="property-name" className="text-sm font-medium mb-2 block">
                  Property Name
                </Label>
                <Input
                  id="property-name"
                  placeholder="e.g., Sunset Villa"
                  value={propertyName}
                  onChange={(e) => setPropertyName(e.target.value)}
                  className="bg-background border-border"
                />
              </div>

              <div>
                <Label className="text-sm font-medium mb-3 block">Property Type</Label>
                <div className="grid grid-cols-2 gap-2">
                  {propertyTypes.map((type) => {
                    const Icon = type.icon
                    const isSelected = propertyType === type.id
                    return (
                      <Button
                        key={type.id}
                        variant="outline"
                        className={`transition-all ${
                          isSelected
                            ? "bg-accent text-accent-foreground border-accent shadow-lg hover:bg-accent/90"
                            : "bg-card text-foreground border-border hover:bg-accent/10 hover:border-accent/50"
                        }`}
                        onClick={() => setPropertyType(type.id as PropertyType)}
                      >
                        <Icon className="w-4 h-4 mr-2" />
                        {type.name}
                      </Button>
                    )
                  })}
                </div>
              </div>
            </Card>
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Platform Selector */}
            <Card className="bg-card border-border p-6">
              <Label className="text-sm font-medium mb-4 block">Choose Platform</Label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {platforms.map((platform) => {
                  const isSelected = selectedPlatform === platform.id
                  return (
                    <button
                      key={platform.id}
                      onClick={() => setSelectedPlatform(platform.id as Platform)}
                      className={`p-4 rounded-lg transition-all text-left ${
                        isSelected
                          ? "border-2 border-accent bg-accent shadow-lg"
                          : "border-2 border-border bg-card hover:bg-accent/10 hover:border-accent/50"
                      }`}
                    >
                      <div className="text-2xl mb-2">{platform.icon}</div>
                      <div
                        className={`text-sm font-medium mb-1 ${isSelected ? "text-accent-foreground" : "text-foreground"}`}
                      >
                        {platform.name}
                      </div>
                      <div className={`text-xs ${isSelected ? "text-accent-foreground/80" : "text-muted-foreground"}`}>
                        {platform.desc}
                      </div>
                    </button>
                  )
                })}
              </div>
            </Card>

            {/* Choose Your Vibe */}
            <Card className="bg-card border-border p-6">
              <Label className="text-sm font-medium mb-4 block">Choose Your Vibe</Label>
              <div className="grid grid-cols-2 gap-3">
                {vibes.map((vibe) => {
                  const isSelected = selectedVibe === vibe.id
                  return (
                    <button
                      key={vibe.id}
                      onClick={() => setSelectedVibe(vibe.id as Vibe)}
                      className={`p-4 rounded-lg transition-all text-left ${
                        isSelected
                          ? "border-2 border-accent bg-accent shadow-lg"
                          : "border-2 border-border bg-card hover:bg-accent/10 hover:border-accent/50"
                      }`}
                    >
                      <div
                        className={`text-sm font-medium mb-1 ${isSelected ? "text-accent-foreground" : "text-foreground"}`}
                      >
                        {vibe.name}
                      </div>
                      <div className={`text-xs ${isSelected ? "text-accent-foreground/80" : "text-muted-foreground"}`}>
                        {vibe.desc}
                      </div>
                    </button>
                  )
                })}
              </div>
            </Card>

            {/* Advanced Options */}
            <Card className="bg-card border-border p-6">
              <Collapsible open={advancedOpen} onOpenChange={setAdvancedOpen}>
                <CollapsibleTrigger className="flex items-center justify-between w-full">
                  <Label className="text-sm font-medium cursor-pointer">Advanced Options</Label>
                  <ChevronDown className={`w-4 h-4 transition-transform ${advancedOpen ? "rotate-180" : ""}`} />
                </CollapsibleTrigger>
                <CollapsibleContent className="mt-4 space-y-4">
                  <div>
                    <Label htmlFor="opening-text" className="text-sm mb-2 block">
                      Opening Text Overlay
                    </Label>
                    <Input
                      id="opening-text"
                      placeholder="Your next vacation starts here"
                      value={openingText}
                      onChange={(e) => setOpeningText(e.target.value)}
                      className="bg-background border-border"
                    />
                  </div>

                  <div>
                    <Label className="text-sm mb-2 block">Color Mood</Label>
                    <div className="grid grid-cols-4 gap-2">
                      {(["warm", "cool", "natural", "vibrant"] as ColorMood[]).map((mood) => {
                        const isSelected = colorMood === mood
                        return (
                          <Button
                            key={mood}
                            variant="outline"
                            size="sm"
                            className={`transition-all ${
                              isSelected
                                ? "bg-accent text-accent-foreground border-accent hover:bg-accent/90"
                                : "bg-background hover:bg-muted border-border text-foreground"
                            }`}
                            onClick={() => setColorMood(mood)}
                          >
                            {mood.charAt(0).toUpperCase() + mood.slice(1)}
                          </Button>
                        )
                      })}
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="music-mood" className="text-sm mb-2 block">
                      Music Mood
                    </Label>
                    <Select value={musicMood} onValueChange={setMusicMood}>
                      <SelectTrigger className="bg-background border-border">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">None</SelectItem>
                        <SelectItem value="upbeat">Upbeat</SelectItem>
                        <SelectItem value="chill">Chill</SelectItem>
                        <SelectItem value="luxurious">Luxurious</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="cta-text" className="text-sm mb-2 block">
                      Call-to-Action
                    </Label>
                    <Input
                      id="cta-text"
                      placeholder="Book Now"
                      value={ctaText}
                      onChange={(e) => setCtaText(e.target.value)}
                      className="bg-background border-border"
                    />
                  </div>
                </CollapsibleContent>
              </Collapsible>
            </Card>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="mt-8 space-y-6">
          {/* Smart Suggestions */}
          {photos.length === 3 && (
            <Card className="bg-accent/5 border-accent/20 p-4">
              <div className="flex flex-wrap gap-4">
                {smartSuggestions.map((suggestion, idx) => {
                  const Icon = suggestion.icon
                  return (
                    <div key={idx} className="flex items-center gap-2">
                      <Icon className="w-4 h-4 text-accent" />
                      <span className="text-sm">{suggestion.text}</span>
                    </div>
                  )
                })}
              </div>
            </Card>
          )}

          {/* Generate Button or Progress */}
          {!videoGenerated ? (
            <div className="space-y-4">
              {isGenerating ? (
                <Card className="bg-card border-border p-6">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span>{getStepText()}</span>
                      <span className="text-muted-foreground">{Math.round(progress)}%</span>
                    </div>
                    <Progress value={progress} className="h-2" />
                  </div>
                </Card>
              ) : (
                <>
                  <Button
                    size="lg"
                    disabled={photos.length === 0 || !propertyName.trim()}
                    onClick={handleGenerate}
                    className="w-full bg-gradient-to-r from-accent to-orange-600 hover:from-accent/90 hover:to-orange-700 text-accent-foreground font-semibold text-lg py-6 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Generate Property Video
                  </Button>
                  {(photos.length === 0 || !propertyName.trim()) && (
                    <p className="text-sm text-muted-foreground text-center">
                      {photos.length === 0 ? "Please upload at least one photo" : "Please enter a property name"}
                    </p>
                  )}
                  <div className="flex items-center gap-6 justify-center">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <Checkbox
                        checked={createABTest}
                        onCheckedChange={(checked) => setCreateABTest(checked as boolean)}
                      />
                      <span className="text-sm">Create A/B test version</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <Checkbox
                        checked={addToSchedule}
                        onCheckedChange={(checked) => setAddToSchedule(checked as boolean)}
                      />
                      <span className="text-sm">Add to posting schedule</span>
                    </label>
                  </div>
                </>
              )}
            </div>
          ) : (
            <Card className="bg-card border-border p-6">
              <div className="space-y-4">
                {error && (
                  <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-sm">
                    Error: {error}
                  </div>
                )}
                {generatedCharacter ? (
                  <div className="aspect-video bg-black rounded-lg overflow-hidden relative">
                    <video
                      controls
                      className="w-full h-full object-cover"
                      src={`${API_BASE_URL}/characters/${generatedCharacter.id}/video`}
                      poster=""
                    >
                      Your browser does not support the video tag.
                    </video>
                    <div className="absolute top-4 left-4 bg-black/50 backdrop-blur-sm px-3 py-1 rounded-full text-white text-sm">
                      {generatedCharacter.name}
                    </div>
                  </div>
                ) : (
                  <div className="aspect-video bg-black rounded-lg flex items-center justify-center relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-accent/20 to-purple-500/20" />
                    <Play className="w-16 h-16 text-white/80" />
                    <p className="absolute bottom-4 left-4 text-sm text-white/60">Your video is ready!</p>
                  </div>
                )}
                <div className="flex flex-wrap gap-3">
                  {generatedCharacter && (
                    <a
                      href={`${API_BASE_URL}/characters/${generatedCharacter.id}/video`}
                      download={`${generatedCharacter.name}_video.mp4`}
                    >
                      <Button className="bg-accent hover:bg-accent/90 text-accent-foreground">
                        <Download className="w-4 h-4 mr-2" />
                        Download
                      </Button>
                    </a>
                  )}
                  <Button variant="outline" className="bg-card border-border hover:bg-muted">
                    <Share2 className="w-4 h-4 mr-2" />
                    Share to {selectedPlatform || "Platform"}
                  </Button>
                  <Button
                    variant="ghost"
                    onClick={() => {
                      setVideoGenerated(false)
                      setGeneratedCharacter(null)
                      setProgress(0)
                      setError(null)
                    }}
                  >
                    <RotateCcw className="w-4 h-4 mr-2" />
                    Try Another Style
                  </Button>
                </div>
              </div>
            </Card>
          )}
        </div>

        {/* Add Yourself Modal */}
        {showAddYourself && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <Card className="bg-card border-border p-6 max-w-md w-full">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Add Yourself to the Scene</h3>
                <button
                  onClick={() => setShowAddYourself(false)}
                  className="p-1 rounded-full hover:bg-muted"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              
              <div className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  Upload a photo of yourself to be placed in the first property image. This will create a personalized version for your video.
                </p>
                
                <div className="border-2 border-dashed border-border rounded-lg p-6 text-center">
                  <Upload className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground mb-2">Upload your photo</p>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleUserPhotoSelect}
                    className="block w-full text-sm text-muted-foreground file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-accent file:text-accent-foreground hover:file:bg-accent/90"
                  />
                </div>

                {userPhoto && (
                  <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
                    <div className="w-12 h-12 bg-muted rounded overflow-hidden">
                      <img
                        src={URL.createObjectURL(userPhoto)}
                        alt="Your photo"
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <span className="text-sm flex-1">{userPhoto.name}</span>
                  </div>
                )}

                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    onClick={() => setShowAddYourself(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleCombineImages}
                    disabled={!userPhoto || isCombiningImages}
                    className="flex-1 bg-accent hover:bg-accent/90 text-accent-foreground"
                  >
                    {isCombiningImages ? "Combining..." : "Add to Scene"}
                  </Button>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
