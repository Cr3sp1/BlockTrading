pragma solidity ^0.5.17;

import "./IToken.sol";

contract Token is IToken {

    string private _name;
    string private _symbol;
    uint256 private _decimals;
    address private _Owner;
    uint256 private _total;
    uint256 private exp;
    uint256 private open_day_1;
    uint256 private close_day_1;
    uint256 private open_day_2;
    uint256 private close_day_2;
    uint256 private open_day_3;
    uint256 private close_day_3;
    uint256 private open_day_4;
    uint256 private close_day_4;
    uint256 private open_day_5;
    uint256 private close_day_5;

    mapping(address => uint256) private balances;
    mapping(address => mapping(address => uint256)) private _approve;
    mapping(address => bool) private minters;

    event Transfer(

	address indexed from,
        address indexed to,
        uint256 indexed value

    );

    event Approve(

	address indexed owner,
	address indexed	spender,
	uint256 indexed value

    );

    event Mint(

	address indexed minter,
	address indexed buyer,
	uint256 indexed value

    );

    constructor(string memory name, string memory symbol, uint256 decimals, uint256 total) public {

        _name = name;
        _symbol = symbol;
        _decimals = decimals;
        _Owner = msg.sender;
        exp = 10 ** decimals;
        _total = total * exp;
        balances[msg.sender] = total * exp;
        open_day_1 = 1689577200;
        close_day_1 = open_day_1 + 9 hours;
        open_day_2 = close_day_1 + 15 hours;
        close_day_2 = open_day_2 + 9 hours;
        open_day_3 = close_day_2 + 15 hours;
        close_day_3 = open_day_3 + 9 hours;
        open_day_4 = close_day_3 + 15 hours;
        close_day_4 = open_day_4 + 9 hours;
        open_day_5 = close_day_4 + 15 hours;
        close_day_5 = open_day_5 + 9 hours;
    }

    modifier OnlyOwner() {

        require(_Owner == msg.sender);
        _;

    }

    modifier OnlyMinter() {

        require(minters[msg.sender] == true);
        _;

    }

     modifier Open(){
        require((block.timestamp > open_day_1 && block.timestamp < close_day_1) ||
                (block.timestamp > open_day_2 && block.timestamp < close_day_2) ||
                (block.timestamp > open_day_3 && block.timestamp < close_day_3) ||
                (block.timestamp > open_day_4 && block.timestamp < close_day_4) ||
                (block.timestamp > open_day_5 && block.timestamp < close_day_5),"Is Closed");
                _;
    }

    function add_minter(address a_address) external OnlyOwner {

        minters[a_address] = true;

    }

    function delete_minter(address d_address) external OnlyOwner {

        minters[d_address] = false;

    }

    function mint(address buyer, uint value) external OnlyMinter  {

        balances[buyer] += value;
        _total += value;

	emit Mint(msg.sender, buyer, value);

    }


    function name() public view returns (string memory) {

        return _name;

    }

    function symbol() public view returns (string memory) {

        return _symbol;

    }

    function decimals() public view returns (uint256) {

        return _decimals;

    }

    function totalSupply() public view returns (uint256) {

        return _total;

    }

    function balanceOf(address _address) public view returns (uint256) {

        return balances[_address];

    }

    function transfer(address _to, uint256 _value) public Open returns (bool success)  {

        require(_value <= balances[msg.sender]);

        balances[_to] += _value;
        balances[msg.sender] -= _value;

	emit Transfer(msg.sender, _to, _value);

        return true;

    }

    function approve(address _spender, uint256 _value) public returns (bool success)  {

        require(_value * exp <= balances[msg.sender]);
        _approve[msg.sender][_spender] = _value * exp;

	emit Approve(msg.sender, _spender, _value * exp);

        return true;

    }

    function allowance(address _owner, address _spender) public view returns (uint256 remaining) {

        return _approve[_owner][_spender];

    }

    function transferFrom(address _from, address _to, uint256 _value) public Open returns (bool success)  {

        require(_value <= balances[_from]);
        require(_value <= allowance(_from, msg.sender));

        balances[_to] += _value;
        balances[_from] -= _value;
        _approve[_from][msg.sender] -= _value;

	emit Transfer(_from, _to, _value);

        return true;

    }

}
