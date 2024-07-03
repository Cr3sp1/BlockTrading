pragma solidity 0.5.17;


interface IMarketplace {
    // Public Variables
    function owner() external view returns (address);
    function paycoin() external view returns (address);
    function liquidity(address tokenAddress) external view returns (uint256);
    function price(address tokenAddress) external view returns (uint256);
    function k(address tokenAddress) external view returns (uint256);
    function initTokAmount(address tokenAddress) external view returns (uint256);
    function fee() external view returns (uint256);

    // Functions
    function addToken(address tokenAddress, uint256 initialAmount) external;
    function mint_stake(address tokenAddress, uint256 tokenAmount) external;
    function burn_stake(address tokenAddress, uint256 tokenAmount) external;
    function paycoinToToken(address tokenAddress, uint256 paycoinAmount) external view returns (uint256);
    function tokenToPaycoin(address tokenAddress, uint256 tokenAmount) external view returns (uint256);
    function buy(address tokenAddress, uint256 paycoinAmount) external;
    function sell(address tokenAddress, uint256 tokenAmount) external;
    function swap(address tokenAddressIn, address tokenAddressOut, uint256 tokenAmountIn) external;
    function day_mint(address tokenAddress) external;
}
