pragma solidity^0.5.17;

import "./IToken.sol";
import "./IPaycoin.sol";
import "./IPool.sol";

contract Pool is IPool{

    uint256 private Token_Amount;
    uint256 private Paycoin_Amount;
    uint256 private price;
    address private _owner;
    uint256 private Tok_in_Amount;
    uint256 private Pay_in_Amount;
    address private pool;
    address private token;
    address private paycoin;
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
    uint256 private exp;
    uint256 private check = 1;
    uint256 private k;
    mapping(address => uint256) private fee;

    event Mint(address indexed _from, uint256 indexed Amount_in);
    event Burn(address indexed _from, uint256 indexed Amount_out);
    event Buy(address indexed _from, uint256 indexed Amount_out);
    event Sell(address indexed _from, uint256 indexed Amount_in);
     

    constructor(address _token, address _paycoin) public{
        Tok_in_Amount = 0;
        Pay_in_Amount = 0;
         _owner = msg.sender;
        Token_Amount = Tok_in_Amount;
        Paycoin_Amount = Pay_in_Amount;
        paycoin = _paycoin;
        token = _token;
        exp = 10 ** IToken(token).decimals();
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

    modifier OnlyOwner(){
        require(msg.sender == _owner);
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

    function add_address(address pl_address) OnlyOwner() external {
        pool = pl_address;
    }

    function mint_liquidity(uint256 token_Am, uint256 Paycoin_Am) OnlyOwner public{
        require(Tok_in_Amount == 0 && Pay_in_Amount == 0);
        IToken(token).mint(pool,token_Am * exp );
        IPaycoin(paycoin).mint(pool,Paycoin_Am * exp);
        Pay_in_Amount += Paycoin_Am * exp ;
        Tok_in_Amount += token_Am * exp;
        Token_Amount += token_Am * exp;
        Paycoin_Amount += Paycoin_Am * exp;
        price = Pay_in_Amount * exp /Tok_in_Amount ;
        k = Tok_in_Amount * Pay_in_Amount ;
    } 

    function day_mint() external Open OnlyOwner{
        uint256 day;
        if(block.timestamp > open_day_1 + 4 hours && block.timestamp < close_day_1){
            day = 1;
        }
        if(block.timestamp > open_day_2 + 4 hours && block.timestamp < close_day_2){
            day = 2;
        }
        if(block.timestamp > open_day_3 + 4 hours && block.timestamp < close_day_3){
            day = 3;
        }
        if(block.timestamp > open_day_2 + 4 hours && block.timestamp < close_day_4){
            day = 4;
        }
        if(block.timestamp > open_day_5 + 4 hours && block.timestamp < close_day_5){
            day = 5;
        }
        require(check <= day);
        IToken(token).mint(msg.sender, day * Tok_in_Amount / 10);
        check = day + 1;           
    }

    function mint_stake(uint256 Amount_in) OnlyOwner() Open public{
        require(Amount_in * exp + Token_Amount < Tok_in_Amount + Tok_in_Amount / 2);
        require(Token_Amount + Amount_in * exp > Tok_in_Amount - Tok_in_Amount / 2);
        IPaycoin(paycoin).transferFrom(_owner, pool, Amount_in  * price);
        IToken(token).transferFrom(_owner, pool, Amount_in * exp);
        Token_Amount += Amount_in * exp;
        Paycoin_Amount += Amount_in * price ;
        k = Paycoin_Amount * Token_Amount;
        emit Mint(msg.sender, Amount_in * exp);
    } 

    function burn_stake(uint256 Amount_out) OnlyOwner() Open public{
        require(Token_Amount - Amount_out * exp > Tok_in_Amount - Tok_in_Amount / 2);
        require(Token_Amount - Amount_out * exp < Tok_in_Amount + Tok_in_Amount / 2);
        IPaycoin(paycoin).transfer(_owner, Amount_out  *  price);
        IToken(token).transfer(_owner, Amount_out * exp );
        Token_Amount -= Amount_out * exp;
        Paycoin_Amount -= Amount_out * price ;
        k = Paycoin_Amount * Token_Amount;
        emit Burn(msg.sender, Amount_out * exp);
    }
    
    function view_price() public view returns(uint256) {
        return price;
    }

    function view_token_amount() external view returns(uint256) {
        return Token_Amount;
    }

    function view_paycoin_amount() external view returns(uint256) {
        return Paycoin_Amount;
    }

    function view_fee(address _buyer) external view returns(uint256){
        return fee[_buyer];
    }

    function buy(uint256 Amount_out) Open public {
        require(msg.sender != _owner, "You can't buy your tokens!!");
        IPaycoin(paycoin).transferFrom(msg.sender, pool, get_Paycoin(Amount_out * exp, true));
        IToken(token).transfer( msg.sender, Amount_out * exp);
        IPaycoin(paycoin).transferFrom(msg.sender, _owner, get_fee(Amount_out * exp,true));
        fee[msg.sender] += get_fee(Amount_out * exp,true);
        Paycoin_Amount += get_Paycoin(Amount_out * exp,true);
        Token_Amount -= Amount_out * exp;
        price = Paycoin_Amount * exp / Token_Amount;
        emit Buy(msg.sender, Amount_out * exp);
    }

    function sell (uint256 Amount_in) Open public {
        require(msg.sender != _owner, "You can't sell your tokens!!!");
        IToken(token).transferFrom(msg.sender, pool, Amount_in * exp);
        IPaycoin(paycoin).transfer(msg.sender, get_Paycoin(Amount_in * exp,false)-get_fee(Amount_in * exp,false));
        IPaycoin(paycoin).transfer(_owner,get_fee(Amount_in*exp,false));
        fee[msg.sender] += get_fee(Amount_in * exp, false);
        Paycoin_Amount -= get_Paycoin(Amount_in * exp, false);
        Token_Amount += Amount_in * exp;
        price = Paycoin_Amount * exp / Token_Amount;
        emit Sell(msg.sender, Amount_in * exp);
    }

    function get_Paycoin(uint256 Amount, bool from_buyer) public view returns(uint256){
        if(from_buyer == true){
            return k  / (Token_Amount - Amount) - Paycoin_Amount ;
        }
        else {
            return Paycoin_Amount - k / (Token_Amount + Amount);
        }
    }
    
    function get_fee(uint256 Amount, bool from_buyer) public view returns(uint256){
            return get_Paycoin(Amount, from_buyer) * 3 / 1000;
    }
}