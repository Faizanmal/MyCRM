'use client';

import { useState } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Shield, Smartphone, AlertCircle, CheckCircle2, Key } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';

export default function TwoFactorAuthPage() {
  const { user, refreshUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [setupMode, setSetupMode] = useState(false);
  const [qrCode, setQrCode] = useState('');
  const [secret, setSecret] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSetup2FA = async () => {
    try {
      setLoading(true);
      setError('');
      
      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        'http://localhost:8000/api/auth/users/setup_2fa/',
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      setQrCode(response.data.qr_code);
      setSecret(response.data.secret);
      setSetupMode(true);
      setSuccess('Scan the QR code with your authenticator app');
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.error || 'Failed to setup 2FA');
      } else {
        setError('Failed to setup 2FA');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleVerify2FA = async () => {
    try {
      setLoading(true);
      setError('');
      
      const token = localStorage.getItem('access_token');
      await axios.post(
        'http://localhost:8000/api/auth/users/verify_2fa/',
        { token: verificationCode },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      setSuccess('2FA enabled successfully!');
      setSetupMode(false);
      setVerificationCode('');
      await refreshUser();
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.error || 'Invalid verification code');
      } else {
        setError('Invalid verification code');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDisable2FA = async () => {
    if (!confirm('Are you sure you want to disable Two-Factor Authentication?')) {
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const token = localStorage.getItem('access_token');
      await axios.post(
        'http://localhost:8000/api/auth/users/disable_2fa/',
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      setSuccess('2FA disabled successfully');
      await refreshUser();
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.error || 'Failed to disable 2FA');
      } else {
        setError('Failed to disable 2FA');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-4 lg:p-6 space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Shield className="h-8 w-8 text-blue-600" />
              Two-Factor Authentication
            </h1>
            <p className="text-gray-500 mt-1">
              Add an extra layer of security to your account
            </p>
          </div>

          {/* Alerts */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert className="border-green-500 text-green-700">
              <CheckCircle2 className="h-4 w-4" />
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}

          {/* Status Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Smartphone className="h-5 w-5" />
                    2FA Status
                  </CardTitle>
                  <CardDescription>
                    Current authentication status
                  </CardDescription>
                </div>
                {user?.two_factor_enabled ? (
                  <Badge className="bg-green-500">Enabled</Badge>
                ) : (
                  <Badge variant="secondary">Disabled</Badge>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h3 className="font-semibold text-blue-900 mb-2">
                  What is Two-Factor Authentication?
                </h3>
                <p className="text-sm text-blue-700">
                  2FA adds an extra layer of security to your account. After entering your password,
                  you&apos;ll need to enter a code from your authenticator app to complete login.
                </p>
              </div>

              {!user?.two_factor_enabled && !setupMode && (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <h3 className="font-semibold">Get Started</h3>
                    <p className="text-sm text-gray-600">
                      You&apos;ll need an authenticator app like:
                    </p>
                    <ul className="text-sm text-gray-600 list-disc list-inside space-y-1">
                      <li>Google Authenticator</li>
                      <li>Microsoft Authenticator</li>
                      <li>Authy</li>
                      <li>1Password</li>
                    </ul>
                  </div>

                  <Button 
                    onClick={handleSetup2FA} 
                    disabled={loading}
                    className="w-full"
                  >
                    <Key className="w-4 h-4 mr-2" />
                    {loading ? 'Setting up...' : 'Enable 2FA'}
                  </Button>
                </div>
              )}

              {setupMode && (
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold mb-2">Step 1: Scan QR Code</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Open your authenticator app and scan this QR code
                    </p>
                      <div className="flex justify-center p-4 bg-white border rounded-lg">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={qrCode} alt="2FA QR Code" className="w-64 h-64" />
                      </div>
                  </div>

                  <div>
                    <h3 className="font-semibold mb-2">Step 2: Enter Secret Key (Optional)</h3>
                    <p className="text-sm text-gray-600 mb-2">
                      If you can&apos;t scan the QR code, enter this secret key manually:
                    </p>
                    <div className="p-3 bg-gray-100 border rounded font-mono text-sm break-all">
                      {secret}
                    </div>
                  </div>

                  <div>
                    <h3 className="font-semibold mb-2">Step 3: Verify Code</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Enter the 6-digit code from your authenticator app
                    </p>
                    <div className="space-y-2">
                      <Label htmlFor="verificationCode">Verification Code</Label>
                      <Input
                        id="verificationCode"
                        type="text"
                        placeholder="000000"
                        maxLength={6}
                        value={verificationCode}
                        onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, ''))}
                        className="text-center text-2xl tracking-widest font-mono"
                      />
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button 
                      onClick={handleVerify2FA} 
                      disabled={loading || verificationCode.length !== 6}
                      className="flex-1"
                    >
                      {loading ? 'Verifying...' : 'Verify & Enable'}
                    </Button>
                    <Button 
                      variant="outline" 
                      onClick={() => {
                        setSetupMode(false);
                        setVerificationCode('');
                        setError('');
                      }}
                      disabled={loading}
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              )}

              {user?.two_factor_enabled && !setupMode && (
                <div className="space-y-4">
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-start gap-3">
                      <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5" />
                      <div>
                        <h3 className="font-semibold text-green-900">
                          2FA is Active
                        </h3>
                        <p className="text-sm text-green-700 mt-1">
                          Your account is protected with two-factor authentication.
                          You&apos;ll need your authenticator app code to sign in.
                        </p>
                      </div>
                    </div>
                  </div>

                  <Button 
                    variant="destructive" 
                    onClick={handleDisable2FA}
                    disabled={loading}
                    className="w-full"
                  >
                    {loading ? 'Disabling...' : 'Disable 2FA'}
                  </Button>

                  <p className="text-xs text-gray-500 text-center">
                    Warning: Disabling 2FA will make your account less secure
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Security Tips */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Security Tips
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5 shrink-0" />
                  <div>
                    <p className="font-medium">Keep backup codes safe</p>
                    <p className="text-sm text-gray-600">
                      Store your backup codes in a secure location in case you lose access to your authenticator app
                    </p>
                  </div>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5 shrink-0" />
                  <div>
                    <p className="font-medium">Use a strong password</p>
                    <p className="text-sm text-gray-600">
                      Combine 2FA with a strong, unique password for maximum security
                    </p>
                  </div>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5 shrink-0" />
                  <div>
                    <p className="font-medium">Don&apos;t share codes</p>
                    <p className="text-sm text-gray-600">
                      Never share your authentication codes with anyone, including support staff
                    </p>
                  </div>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
