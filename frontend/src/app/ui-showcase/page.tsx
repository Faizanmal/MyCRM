'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ThemeToggle } from '@/components/ThemeToggle';
import { 
  Sparkles, 
  Zap, 
  Heart, 
  Star,
  TrendingUp,
  Users,
  DollarSign,
  Target
} from 'lucide-react';

export default function UIShowcasePage() {
  return (
    <div className="min-h-screen p-8 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-5xl font-bold gradient-text">
          Modern UI Showcase
        </h1>
        <p className="text-muted-foreground text-lg">
          Explore the new dark theme and modern design system
        </p>
        <div className="flex justify-center gap-4">
          <ThemeToggle />
          <Badge variant="outline" className="px-4 py-2">
            <Sparkles className="w-4 h-4 mr-2" />
            Dark Theme Enabled
          </Badge>
        </div>
      </div>

      {/* Glass Cards */}
      <section className="space-y-4">
        <h2 className="text-3xl font-bold">Glass Morphism Cards</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="glass p-6 rounded-2xl">
            <h3 className="text-xl font-bold mb-2">Frosted Glass</h3>
            <p className="text-muted-foreground">Beautiful backdrop blur effect with semi-transparent background</p>
          </div>
          <div className="glass p-6 rounded-2xl">
            <h3 className="text-xl font-bold mb-2">Modern Design</h3>
            <p className="text-muted-foreground">Clean and elegant with subtle borders</p>
          </div>
          <div className="glass p-6 rounded-2xl">
            <h3 className="text-xl font-bold mb-2">Depth & Layer</h3>
            <p className="text-muted-foreground">Creates visual hierarchy and depth</p>
          </div>
        </div>
      </section>

      {/* Modern Cards with Hover Effects */}
      <section className="space-y-4">
        <h2 className="text-3xl font-bold">Modern Cards</h2>
        <div className="grid md:grid-cols-4 gap-6">
          {[
            { title: 'Total Users', value: '2,543', icon: Users, color: 'from-blue-500 to-blue-600' },
            { title: 'Revenue', value: '$45.2K', icon: DollarSign, color: 'from-green-500 to-green-600' },
            { title: 'Growth', value: '+23%', icon: TrendingUp, color: 'from-purple-500 to-purple-600' },
            { title: 'Goals', value: '95%', icon: Target, color: 'from-pink-500 to-pink-600' },
          ].map((stat, i) => (
            <Card key={i} className="modern-card hover:scale-105 transition-transform duration-300 group">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <div className={`p-2 rounded-xl bg-linear-to-r ${stat.color} group-hover:scale-110 transition-transform`}>
                  <stat.icon className="h-4 w-4 text-white" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold gradient-text">{stat.value}</div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Gradient Backgrounds */}
      <section className="space-y-4">
        <h2 className="text-3xl font-bold">Gradient Backgrounds</h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="relative overflow-hidden rounded-2xl p-8 bg-linear-to-br from-blue-600 via-purple-600 to-pink-600 text-white shadow-2xl">
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32 blur-3xl"></div>
            <div className="relative z-10">
              <Sparkles className="w-12 h-12 mb-4" />
              <h3 className="text-2xl font-bold mb-2">Multi-Color Gradient</h3>
              <p className="text-blue-50">Beautiful blend of blue, purple, and pink</p>
            </div>
          </div>

          <div className="animated-gradient rounded-2xl p-8">
            <Zap className="w-12 h-12 mb-4 text-primary" />
            <h3 className="text-2xl font-bold mb-2">Animated Gradient</h3>
            <p className="text-muted-foreground">Subtle background animation that creates movement</p>
          </div>
        </div>
      </section>

      {/* Gradient Text Examples */}
      <section className="space-y-4">
        <h2 className="text-3xl font-bold">Gradient Text</h2>
        <div className="space-y-6 text-center">
          <h1 className="text-6xl font-bold gradient-text">
            Stunning Headlines
          </h1>
          <h2 className="text-4xl font-bold gradient-text">
            Beautiful Subheadings
          </h2>
          <p className="text-2xl gradient-text">
            Even paragraphs can have gradients!
          </p>
        </div>
      </section>

      {/* Buttons & Interactive Elements */}
      <section className="space-y-4">
        <h2 className="text-3xl font-bold">Interactive Elements</h2>
        <div className="flex flex-wrap gap-4">
          <Button size="lg" className="bg-linear-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
            <Sparkles className="w-4 h-4 mr-2" />
            Primary Action
          </Button>
          <Button size="lg" variant="outline">
            <Heart className="w-4 h-4 mr-2" />
            Secondary Action
          </Button>
          <Button size="lg" variant="ghost">
            <Star className="w-4 h-4 mr-2" />
            Ghost Button
          </Button>
        </div>
      </section>

      {/* Badges */}
      <section className="space-y-4">
        <h2 className="text-3xl font-bold">Badges & Tags</h2>
        <div className="flex flex-wrap gap-3">
          <Badge className="bg-linear-to-r from-blue-500 to-blue-600 text-white">New</Badge>
          <Badge className="bg-linear-to-r from-green-500 to-green-600 text-white">Success</Badge>
          <Badge className="bg-linear-to-r from-purple-500 to-purple-600 text-white">Featured</Badge>
          <Badge className="bg-linear-to-r from-pink-500 to-pink-600 text-white">Popular</Badge>
          <Badge variant="outline">Outlined</Badge>
        </div>
      </section>

      {/* Theme Comparison */}
      <section className="space-y-4">
        <h2 className="text-3xl font-bold">Theme Features</h2>
        <div className="grid md:grid-cols-2 gap-6">
          <Card className="modern-card">
            <CardHeader>
              <CardTitle>🌞 Light Mode</CardTitle>
              <CardDescription>Clean and bright interface</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-sm">✓ Soft shadows and borders</p>
              <p className="text-sm">✓ High contrast for readability</p>
              <p className="text-sm">✓ Blue/purple gradient accents</p>
              <p className="text-sm">✓ Professional appearance</p>
            </CardContent>
          </Card>

          <Card className="modern-card">
            <CardHeader>
              <CardTitle>🌙 Dark Mode</CardTitle>
              <CardDescription>Easy on the eyes</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-sm">✓ Deep, rich backgrounds</p>
              <p className="text-sm">✓ Enhanced contrast</p>
              <p className="text-sm">✓ Vibrant accent colors</p>
              <p className="text-sm">✓ Reduced eye strain</p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <div className="text-center py-12">
        <p className="text-muted-foreground">
          Toggle between themes using the button in the header to see all these effects in action!
        </p>
      </div>
    </div>
  );
}
