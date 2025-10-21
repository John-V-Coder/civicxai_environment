/**
 * Network Configurations for Wallet Connect
 * Includes Ethereum, Polygon, Fetch.ai, and other supported networks
 */

export const NETWORKS = {
  // Ethereum Networks
  ETHEREUM_MAINNET: {
    chainId: '0x1',
    chainName: 'Ethereum Mainnet',
    nativeCurrency: {
      name: 'Ether',
      symbol: 'ETH',
      decimals: 18
    },
    rpcUrls: ['https://mainnet.infura.io/v3/'],
    blockExplorerUrls: ['https://etherscan.io']
  },

  SEPOLIA_TESTNET: {
    chainId: '0xaa36a7',
    chainName: 'Sepolia Testnet',
    nativeCurrency: {
      name: 'Sepolia Ether',
      symbol: 'SepoliaETH',
      decimals: 18
    },
    rpcUrls: ['https://sepolia.infura.io/v3/'],
    blockExplorerUrls: ['https://sepolia.etherscan.io']
  },

  // Polygon Networks
  POLYGON_MAINNET: {
    chainId: '0x89',
    chainName: 'Polygon Mainnet',
    nativeCurrency: {
      name: 'MATIC',
      symbol: 'MATIC',
      decimals: 18
    },
    rpcUrls: ['https://polygon-rpc.com'],
    blockExplorerUrls: ['https://polygonscan.com']
  },

  POLYGON_MUMBAI: {
    chainId: '0x13881',
    chainName: 'Polygon Mumbai Testnet',
    nativeCurrency: {
      name: 'MATIC',
      symbol: 'MATIC',
      decimals: 18
    },
    rpcUrls: ['https://rpc-mumbai.maticvigil.com'],
    blockExplorerUrls: ['https://mumbai.polygonscan.com']
  },

  // Base Network
  BASE_MAINNET: {
    chainId: '0x2105',
    chainName: 'Base',
    nativeCurrency: {
      name: 'Ether',
      symbol: 'ETH',
      decimals: 18
    },
    rpcUrls: ['https://mainnet.base.org'],
    blockExplorerUrls: ['https://basescan.org']
  },

  // Fetch.ai Network (ASI Alliance)
  FETCHAI_MAINNET: {
    chainId: '0xfc', // 252 in decimal
    chainName: 'Fetch.ai Mainnet',
    nativeCurrency: {
      name: 'FET',
      symbol: 'FET',
      decimals: 18
    },
    rpcUrls: ['https://rpc-fetchhub.fetch.ai:443'],
    blockExplorerUrls: ['https://explore-fetchhub.fetch.ai']
  },

  FETCHAI_TESTNET: {
    chainId: '0xfd', // 253 in decimal
    chainName: 'Fetch.ai Testnet',
    nativeCurrency: {
      name: 'testFET',
      symbol: 'testFET',
      decimals: 18
    },
    rpcUrls: ['https://rpc-dorado.fetch.ai:443'],
    blockExplorerUrls: ['https://explore-dorado.fetch.ai']
  }
};

/**
 * Get network configuration by chain ID
 */
export const getNetworkByChainId = (chainId) => {
  return Object.values(NETWORKS).find(network => network.chainId === chainId);
};

/**
 * Get network name by chain ID
 */
export const getNetworkName = (chainId) => {
  const networkNames = {
    '0x1': 'Ethereum',
    '0x5': 'Goerli',
    '0xaa36a7': 'Sepolia',
    '0x89': 'Polygon',
    '0x13881': 'Mumbai',
    '0x2105': 'Base',
    '0xfc': 'Fetch.ai',
    '0xfd': 'Fetch.ai Testnet'
  };
  return networkNames[chainId] || 'Unknown Network';
};

/**
 * Check if current network is supported
 */
export const isSupportedNetwork = (chainId) => {
  return Object.values(NETWORKS).some(network => network.chainId === chainId);
};

/**
 * Default network for the application
 */
export const DEFAULT_NETWORK = NETWORKS.SEPOLIA_TESTNET;

export default NETWORKS;
