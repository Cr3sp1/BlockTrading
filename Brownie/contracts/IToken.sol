pragma solidity 0.5.17;

interface IToken {
    
    function balanceOf( address account ) external view returns(uint256);

    function owner() external view returns (address);

    function transfer( uint256 amount, address recipient ) external;

    function approve( uint256 amount, address recipient ) external;

    function transferFrom( uint256 amount, address sender, address recipient ) external;

    function allowance( address giver, address spender ) external view returns (uint256);

    function setMinter( address newMinter ) external;

    function deleteMinter( address exMinter ) external;

    function minting( address recipient, uint256 amount ) external;

    function burn( address recipient, uint256 amount ) external;
    
}