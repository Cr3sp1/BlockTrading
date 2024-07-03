pragma solidity ^0.5.17;

interface IToken {

	function mint(address buyer, uint256 value) external;

	function transfer(address _to, uint256 value) external returns (bool success);

	function transferFrom(address _from, address _to, uint256 value) external returns (bool success);

	function decimals() external view returns (uint256);

	function approve(address _spender, uint256 _value) external returns (bool success);
	
	function add_minter(address a_address) external;

	function balanceOf(address _address) external view returns (uint256);
}
