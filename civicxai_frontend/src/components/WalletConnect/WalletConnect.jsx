import React from 'react';
import { Wallet, LogOut, CircleDollarSign } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { useWalletConnect } from '@/hooks/useWalletConnect';
import { getNetworkName } from '@/config/networks';

/**
 * Wallet Connect Component
 * Provides wallet connection UI with dropdown for connected state
 * Supports MetaMask and Web3 wallets with Fetch.ai/ASI network compatibility
 */
export const WalletConnect = () => {
  const {
    isConnected,
    account,
    balance,
    chainId,
    loading,
    isWalletInstalled,
    connect,
    disconnect,
    getBalance,
  } = useWalletConnect();

  // Format address for display
  const formatAddress = (address) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  // Format balance for display
  const formatBalance = (balance) => {
    if (balance === null || balance === undefined) return '0.0000';
    return balance.toFixed(4);
  };

  if (!isWalletInstalled) {
    return (
      <Button
        variant="outline"
        onClick={() => window.open('https://metamask.io/download/', '_blank')}
        className="bg-slate-800 border-slate-700 text-white hover:bg-slate-700"
      >
        <Wallet className="mr-2 h-4 w-4" />
        Install Wallet
      </Button>
    );
  }

  if (!isConnected) {
    return (
      <Button
        onClick={connect}
        disabled={loading}
        className="bg-blue-600 hover:bg-blue-700 text-white"
      >
        <Wallet className="mr-2 h-4 w-4" />
        {loading ? 'Connecting...' : 'Connect Wallet'}
      </Button>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          className="bg-slate-800 border-slate-700 text-white hover:bg-slate-700"
        >
          <Wallet className="mr-2 h-4 w-4" />
          {formatAddress(account)}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="bg-slate-900 border-slate-800 text-white w-64">
        <DropdownMenuLabel>Wallet Info</DropdownMenuLabel>
        <DropdownMenuSeparator className="bg-slate-800" />
        
        <div className="px-2 py-2 space-y-2">
          {/* Address */}
          <div>
            <p className="text-xs text-slate-400">Address</p>
            <p className="text-sm font-mono">{formatAddress(account)}</p>
          </div>

          {/* Balance */}
          <div>
            <p className="text-xs text-slate-400">Balance</p>
            <p className="text-sm font-semibold text-green-500">
              {formatBalance(balance)} ETH
            </p>
          </div>

          {/* Network */}
          {chainId && (
            <div>
              <p className="text-xs text-slate-400">Network</p>
              <Badge variant="secondary" className="mt-1">
                {getNetworkName(chainId)}
              </Badge>
            </div>
          )}
        </div>

        <DropdownMenuSeparator className="bg-slate-800" />
        
        <DropdownMenuItem
          onClick={getBalance}
          className="cursor-pointer hover:bg-slate-800"
        >
          <CircleDollarSign className="mr-2 h-4 w-4" />
          Refresh Balance
        </DropdownMenuItem>
        
        <DropdownMenuItem
          onClick={disconnect}
          className="cursor-pointer hover:bg-slate-800 text-red-400"
        >
          <LogOut className="mr-2 h-4 w-4" />
          Disconnect
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default WalletConnect;
