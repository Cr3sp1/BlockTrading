pragma solidity 0.5.17;

import "./IToken.sol";


contract Token{

    // associa ad ogni indirizzo un int rappresentante il suo bilancio
    mapping( address => uint256 ) private _balance; 

    // numero totale di token in circolazione
    uint256 public totalSupply;

    // matrice che associa ad ogni coppia di indirizzi quanto il secondo può prelevare dal primo
    mapping( address => mapping( address => uint256 ) ) internal _allowance;

    address public owner;

    // nome
    string public name;

    // simbolo
    string public symbol;

    // numero di decimali
    uint256 public decimals = 18;

    mapping( address => bool ) public isMinter;


    // eventi
    event Transfer( address indexed from, address indexed to, uint256 value );
    event Approve( address indexed owner, address indexed spender, uint256 value );
    event Mint( address indexed minter, address indexed buyer, uint256 value );


    constructor( address _owner, string memory _name, string memory _symbol ) public {
        owner = _owner;
        isMinter[owner] = true;
        name = _name;
        symbol = _symbol;
    }


    modifier onlyOwner() {
        require( msg.sender == owner, "You are not the token owner!" );
        _;
    }

    modifier onlyMinter() {
        require( isMinter[msg.sender], "You are not a token minter!" );
        _;
    }
    

    // controlla balance
    function balanceOf( address account ) external view returns(uint256) {
        return _balance[account];
    }


    // funzione che trasferisce
    function transfer( uint256 amount, address recipient ) external {
        require( amount <= _balance[msg.sender], "Insufficient balance!" );
        _balance[msg.sender] -= amount;
        _balance[recipient] += amount;
        emit Transfer( msg.sender, recipient, amount );
    }

    function approve( uint256 amount, address recipient ) external {
        _allowance[msg.sender][recipient] = amount;
        emit Approve( msg.sender, recipient, amount );
    }

    function increaseAllowance( uint256 amount, address recipient ) external {
        _allowance[msg.sender][recipient] += amount;
    }

    function decreaseAllowance( uint256 amount, address recipient ) external {
        require( _allowance[msg.sender][recipient] >= amount, "Insufficient allowance!" );
        _allowance[msg.sender][recipient] -= amount;
    }

    function transferFrom( uint256 amount, address sender, address recipient ) external {
        require( amount <= _allowance[sender][msg.sender], "Insufficient allowance!" );
        require( amount <= _balance[sender], "Insufficient balance!" );
        _allowance[sender][msg.sender] -= amount;
        _balance[sender] -= amount;
        _balance[recipient] += amount;
        emit Transfer( sender, recipient, amount );
    }

    function allowance( address giver, address spender ) external view returns (uint256) {
        return _allowance[giver][spender];
    }

    function setMinter( address newMinter ) external onlyOwner {
        isMinter[newMinter] = true;
    }

    function deleteMinter( address exMinter ) external onlyOwner {
        isMinter[exMinter] = false;
    }

    function minting( address recipient, uint256 amount ) external onlyMinter {
        _balance[recipient] += amount;
        totalSupply += amount;
        emit Mint( msg.sender, recipient, amount );
    }

    function burn( address recipient, uint256 amount ) external onlyMinter {
        require( _balance[recipient] >= amount, "Burning too much!" );
        _balance[recipient] -= amount;
        totalSupply -= amount;
    }
    
}
