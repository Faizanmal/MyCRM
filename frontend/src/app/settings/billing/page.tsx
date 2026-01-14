'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import { CreditCard, Download, AlertCircle, CheckCircle } from 'lucide-react';

import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export default function BillingSettingsPage() {
  const [currentPlan, setCurrentPlan] = useState('pro');

  const plans = [
    {
      id: 'free',
      name: 'Free',
      price: '$0',
      period: 'month',
      description: 'Perfect for getting started',
      features: [
        'Up to 100 contacts',
        'Basic reporting',
        'Email integration',
        'Community support',
      ],
    },
    {
      id: 'pro',
      name: 'Professional',
      price: '$99',
      period: 'month',
      description: 'For growing teams',
      features: [
        'Unlimited contacts',
        'Advanced reporting',
        'AI Sales Assistant',
        'Priority support',
        'Custom integrations',
      ],
      current: true,
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: 'Custom',
      period: 'month',
      description: 'For large organizations',
      features: [
        'Everything in Pro',
        'Dedicated support',
        'Custom development',
        'SLA guarantee',
        'Advanced security',
      ],
    },
  ];

  const handlePlanChange = async (planId: string) => {
    if (planId === currentPlan) {
      toast.info('You are already on this plan');
      return;
    }

    try {
      const response = await fetch('/api/v1/billing/change-plan/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan: planId }),
      });

      if (!response.ok) throw new Error('Failed to change plan');
      
      setCurrentPlan(planId);
      toast.success('Plan changed successfully');
    } catch (error) {
      console.warn("Failed to change plan",error);
      toast.error('Failed to change plan');
    }
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6 max-w-6xl">
          <div>
            <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white">Billing & Subscription</h1>
            <p className="text-gray-500 mt-1">Manage your subscription and billing information</p>
          </div>

          {/* Current Plan */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CreditCard className="w-5 h-5" />
                Current Plan
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-linear-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 p-6 rounded-lg border border-blue-200 dark:border-blue-800">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Professional Plan</h3>
                    <p className="text-gray-600 dark:text-gray-400 mt-1">$99/month • Renews on Jan 15, 2025</p>
                  </div>
                  <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Active</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Plans */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Available Plans</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {plans.map((plan) => (
                <Card key={plan.id} className={plan.current ? 'border-blue-500 border-2' : ''}>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      {plan.name}
                      {plan.current && <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">Current</Badge>}
                    </CardTitle>
                    <CardDescription>{plan.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <span className="text-3xl font-bold text-gray-900 dark:text-white">{plan.price}</span>
                      <span className="text-gray-500 ml-2">/{plan.period}</span>
                    </div>

                    <ul className="space-y-2">
                      {plan.features.map((feature) => (
                        <li key={feature} className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                          <CheckCircle className="w-4 h-4 text-green-500" />
                          {feature}
                        </li>
                      ))}
                    </ul>

                    <Button
                      onClick={() => handlePlanChange(plan.id)}
                      disabled={plan.current}
                      className="w-full"
                      variant={plan.current ? 'outline' : 'default'}
                    >
                      {plan.current ? 'Current Plan' : 'Choose Plan'}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Payment Method */}
          <Card>
            <CardHeader>
              <CardTitle>Payment Method</CardTitle>
              <CardDescription>Update your billing information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 border rounded-lg bg-gray-50 dark:bg-gray-900">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Visa ending in 4242</p>
                    <p className="text-sm text-gray-500">Expires 12/25</p>
                  </div>
                  <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Default</Badge>
                </div>
              </div>
              <Button variant="outline">Update Payment Method</Button>
            </CardContent>
          </Card>

          {/* Invoices */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Download className="w-5 h-5" />
                Invoices
              </CardTitle>
              <CardDescription>Download your past invoices</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { date: 'Jan 15, 2025', amount: '$99.00', status: 'Paid' },
                  { date: 'Dec 15, 2024', amount: '$99.00', status: 'Paid' },
                  { date: 'Nov 15, 2024', amount: '$99.00', status: 'Paid' },
                ].map((invoice, i) => (
                  <div key={i} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{invoice.date}</p>
                      <p className="text-sm text-gray-500">{invoice.amount}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">{invoice.status}</Badge>
                      <Button variant="ghost" size="sm">
                        <Download className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Billing Address */}
          <Card>
            <CardHeader>
              <CardTitle>Billing Address</CardTitle>
              <CardDescription>Update your billing address</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 dark:text-gray-400 mb-4">123 Main Street, City, State 12345</p>
              <Button variant="outline">Edit Billing Address</Button>
            </CardContent>
          </Card>

          {/* Danger Zone */}
          <Card className="border-red-200 dark:border-red-900">
            <CardHeader>
              <CardTitle className="text-red-600 dark:text-red-400">Manage Subscription</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="p-3 border border-red-200 dark:border-red-900 rounded-lg bg-red-50 dark:bg-red-950 flex gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm text-red-800 dark:text-red-200 font-medium">Warning</p>
                  <p className="text-sm text-red-700 dark:text-red-300">Canceling your subscription will disable access to all features.</p>
                </div>
              </div>
              <Button variant="destructive">Cancel Subscription</Button>
            </CardContent>
          </Card>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}

