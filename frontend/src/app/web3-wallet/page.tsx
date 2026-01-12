'use client';

import { useState, useEffect } from 'react';
import { web3API } from '@/lib/new-features-api';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { WalletIcon, KeyIcon, ShieldCheckIcon, SparklesIcon, CubeIcon, LockClosedIcon } from '@heroicons/react/24/outline';

export default function Web3WalletPage() {
  const [wallet, setWallet] = useState<any>(null);
  const [nftRewards, setNftRewards] = useState<any[]>([]);
  const [accessGrants, setAccessGrants] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [walletRes, nftRes, grantsRes] = await Promise.all([
        web3API.getWallets(),
        web3API.getNFTRewards(),
        web3API.getAccessGrants()
      ]);
      const wallets = walletRes.data.results || walletRes.data;
      setWallet(wallets.length > 0 ? wallets[0] : null);
      setNftRewards(nftRes.data.results || nftRes.data);
      setAccessGrants(grantsRes.data.results || grantsRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const createWallet = async () => {
    try {
      const res = await web3API.createWallet();
      setWallet(res.data);
      alert('Data Wallet Created Successfully!');
    } catch (error: any) {
      alert(error.response?.data?.error || 'Failed to create wallet');
    }
  };

  const redeemNFT = async (id: string) => {
    try {
      await web3API.redeemNFT(id);
      alert('NFT Reward Redeemed Successfully!');
      loadData();
    } catch (error) {
      alert('Failed to redeem NFT');
    }
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-2">
                <WalletIcon className="w-8 h-8 text-blue-600" />
                Web3 Data Wallet
              </h1>
              <p className="text-gray-600 mt-1">
                Decentralized data ownership with blockchain security
              </p>
            </div>
          </div>

          {/* Wallet Overview */}
          {!wallet ? (
            <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
              <CardContent className="pt-6">
                <div className="text-center py-8">
                  <WalletIcon className="w-20 h-20 mx-auto mb-4 text-blue-600" />
                  <h3 className="text-xl font-semibold mb-2">Create Your Data Wallet</h3>
                  <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
                    Take control of your data with blockchain-backed ownership. Create a secure data wallet
                    to manage permissions, earn NFT rewards, and participate in the Web3 ecosystem.
                  </p>
                  <Button onClick={createWallet} size="lg" className="bg-blue-600 hover:bg-blue-700">
                    <KeyIcon className="w-5 h-5 mr-2" />
                    Create Data Wallet
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <ShieldCheckIcon className="w-5 h-5 text-green-600" />
                    Wallet Details
                  </CardTitle>
                  <CardDescription>Your blockchain identity</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Wallet Address</label>
                    <div className="mt-1 font-mono text-sm bg-gray-50 p-3 rounded border">
                      {wallet.wallet_address}
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Network</label>
                    <div className="mt-1">
                      <Badge variant="outline" className="capitalize">{wallet.blockchain_network}</Badge>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Status</label>
                    <div className="mt-1">
                      {wallet.is_verified ? (
                        <Badge className="bg-green-600">Verified</Badge>
                      ) : (
                        <Badge variant="secondary">Pending Verification</Badge>
                      )}
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Active Permissions</label>
                    <div className="mt-1 text-sm">
                      {wallet.active_permissions?.length || 0} active grant(s)
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <LockClosedIcon className="w-5 h-5" />
                    Data Access Grants
                  </CardTitle>
                  <CardDescription>Manage temporary access permissions</CardDescription>
                </CardHeader>
                <CardContent>
                  {accessGrants.length === 0 ? (
                    <p className="text-center text-gray-500 py-4">No active grants</p>
                  ) : (
                    <div className="space-y-3">
                      {accessGrants.slice(0, 3).map((grant) => (
                        <div key={grant.id} className="border rounded p-3">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="font-medium">{grant.requester}</div>
                              <div className="text-sm text-gray-600">{grant.purpose}</div>
                              <div className="text-xs text-gray-500 mt-1">
                                Expires: {new Date(grant.expires_at).toLocaleDateString()}
                              </div>
                            </div>
                            <Badge variant={grant.is_active ? 'default' : 'secondary'}>
                              {grant.is_active ? 'Active' : 'Inactive'}
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}

          {/* NFT Rewards */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <SparklesIcon className="w-5 h-5 text-purple-600" />
                NFT Loyalty Rewards
              </CardTitle>
              <CardDescription>Your blockchain-backed achievements</CardDescription>
            </CardHeader>
            <CardContent>
              {nftRewards.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <CubeIcon className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                  <p>No NFT rewards yet. Complete milestones to earn rewards!</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {nftRewards.map((nft) => (
                    <div key={nft.id} className="border rounded-lg p-4 hover:shadow-lg transition-shadow">
                      <div className="aspect-square bg-gradient-to-br from-purple-400 to-pink-600 rounded-lg mb-3 flex items-center justify-center">
                        <SparklesIcon className="w-16 h-16 text-white" />
                      </div>
                      <h3 className="font-semibold mb-1">{nft.reward_name}</h3>
                      <p className="text-sm text-gray-600 mb-2">{nft.description}</p>
                      <div className="flex items-center justify-between">
                        <Badge variant="outline">{nft.points_value} pts</Badge>
                        {!nft.is_redeemed ? (
                          <Button size="sm" onClick={() => redeemNFT(nft.id)}>
                            Redeem
                          </Button>
                        ) : (
                          <Badge className="bg-green-600">Redeemed</Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Info */}
          <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
            <CardContent className="pt-6">
              <h3 className="font-semibold text-lg mb-3">Web3 Benefits</h3>
              <ul className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-700">
                <li className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0" />
                  <span>Full ownership and control of your data via blockchain</span>
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0" />
                  <span>Grant temporary, revocable access to your information</span>
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0" />
                  <span>Earn NFT rewards for engagement milestones</span>
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0" />
                  <span>Smart contracts for automated, trustless agreements</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
