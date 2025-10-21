import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { getNetworkName } from '@/config/networks';

/**
 * Custom hook for wallet connection
 * Supports MetaMask and other Web3 wallets including Fetch.ai/ASI networks
 */
export const useWalletConnect = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [account, setAccount] = useState(null);
  const [balance, setBalance] = useState(null);
  const [provider, setProvider] = useState(null);
  const [chainId, setChainId] = useState(null);
  const [loading, setLoading] = useState(false);

  // Check if wallet is installed
  const isWalletInstalled = () => {
    return typeof window !== 'undefined' && window.ethereum !== undefined;
  };

  // Initialize provider
  useEffect(() => {
    if (isWalletInstalled()) {
      setProvider(window.ethereum);
      
      // Check if already connected
      checkConnection();
      
      // Listen for account changes
      window.ethereum.on('accountsChanged', handleAccountsChanged);
      window.ethereum.on('chainChanged', handleChainChanged);
      
      return () => {
        if (window.ethereum.removeListener) {
          window.ethereum.removeListener('accountsChanged', handleAccountsChanged);
          window.ethereum.removeListener('chainChanged', handleChainChanged);
        }
      };
    }
  }, []);

  const handleAccountsChanged = (accounts) => {
    if (accounts.length === 0) {
      disconnect();
    } else {
      setAccount(accounts[0]);
      getBalance(accounts[0]);
    }
  };

  const handleChainChanged = (newChainId) => {
    setChainId(newChainId);
    window.location.reload(); // Recommended by MetaMask
  };

  const checkConnection = async () => {
    if (!provider) return;
    
    try {
      const accounts = await provider.request({ method: 'eth_accounts' });
      if (accounts.length > 0) {
        setAccount(accounts[0]);
        setIsConnected(true);
        await getBalance(accounts[0]);
        await getChainId();
      }
    } catch (error) {
      console.error('Error checking connection:', error);
    }
  };

  const connect = async () => {
    if (!isWalletInstalled()) {
      toast.error('Please install MetaMask or another Web3 wallet');
      window.open('https://metamask.io/download/', '_blank');
      return;
    }

    setLoading(true);
    
    try {
      const accounts = await provider.request({ 
        method: 'eth_requestAccounts' 
      });
      
      if (accounts.length > 0) {
        setAccount(accounts[0]);
        setIsConnected(true);
        await getBalance(accounts[0]);
        await getChainId();
        toast.success(`Connected: ${accounts[0].slice(0, 6)}...${accounts[0].slice(-4)}`);
      }
    } catch (error) {
      console.error('Connection error:', error);
      if (error.code === 4001) {
        toast.error('Connection rejected');
      } else {
        toast.error('Failed to connect wallet');
      }
    } finally {
      setLoading(false);
    }
  };

  const disconnect = () => {
    setAccount(null);
    setBalance(null);
    setIsConnected(false);
    setChainId(null);
    toast.info('Wallet disconnected');
  };

  const getBalance = async (address) => {
    if (!provider || !address) return;
    
    try {
      const balanceHex = await provider.request({
        method: 'eth_getBalance',
        params: [address, 'latest']
      });
      
      const balanceWei = BigInt(balanceHex);
      const balanceEth = Number(balanceWei) / 10 ** 18;
      setBalance(balanceEth);
    } catch (error) {
      console.error('Error fetching balance:', error);
    }
  };

  const getChainId = async () => {
    if (!provider) return;
    
    try {
      const chainId = await provider.request({ method: 'eth_chainId' });
      setChainId(chainId);
    } catch (error) {
      console.error('Error fetching chain ID:', error);
    }
  };

  const switchNetwork = async (targetChainId) => {
    if (!provider) return;
    
    try {
      await provider.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: targetChainId }],
      });
      toast.success('Network switched');
    } catch (error) {
      console.error('Error switching network:', error);
      toast.error('Failed to switch network');
    }
  };

  const addNetwork = async (networkConfig) => {
    if (!provider) return;
    
    try {
      await provider.request({
        method: 'wallet_addEthereumChain',
        params: [networkConfig],
      });
      toast.success('Network added');
    } catch (error) {
      console.error('Error adding network:', error);
      toast.error('Failed to add network');
    }
  };

  return {
    // State
    isConnected,
    account,
    balance,
    chainId,
    loading,
    isWalletInstalled: isWalletInstalled(),
    
    // Actions
    connect,
    disconnect,
    getBalance: () => getBalance(account),
    switchNetwork,
    addNetwork,
  };
};

export default useWalletConnect;
