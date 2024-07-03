pragma solidity^0.5.17;

interface IPool{
    function add_address(address pl_address) external;

    function mint_liquidity(uint256 token_Am, uint256 Paycoin_Am) external;

    function day_mint() external;

    function mint_stake(uint256 Amount_in) external;

    function burn_stake(uint256 Amount_out) external;

    function view_price() external view returns(uint256);

    function buy(uint256 Amount_out) external;

    function sell (uint256 Amount_in) external;

    function get_Paycoin(uint256 Amount, bool from_buyer) external view returns(uint256);

    function view_fee(address _buyer) external view returns(uint256);

    function get_fee(uint256 Amount, bool from_buyer) external view returns(uint256);
}