pragma solidity 0.5.17;

import "./IToken.sol";
import "./IMarketplace.sol";

contract Marketplace{

    address public owner;

    // paycoin
    IToken paycoin;
    // associa un token (da inizializzare) ad ogni indirizzo
    mapping( address => IToken ) private token;
    // associa la liquidity pool del token ad ogni indirizzo
    mapping( address => uint256 ) public liquidity;
    // associa un prezzo del token ad ogni indirizzo
    mapping( address => uint256 ) public price;
    // associa una k del token ad ogni indirizzo
    mapping( address => uint256 ) public k;
    // associa una quantita' iniziale del token ad ogni indirizzo
    mapping( address => uint256 ) public initTokAmount;

    // fee in decimi di percentuale
    uint256 public fee = 3;
    // orari
    uint256 private open_day_1 = 1719471300;
    uint256 private close_day_1 = open_day_1 + 9 hours;
    uint256 private open_day_2 = open_day_1 + 24 hours;
    uint256 private close_day_2 = open_day_2 + 9 hours;
    uint256 private open_day_3 = open_day_2 + 24 hours;
    uint256 private close_day_3 = open_day_3 + 9 hours;
    uint256 private open_day_4 = open_day_3 + 48 hours;
    uint256 private close_day_4 = open_day_4 + 9 hours;
    uint256 private open_day_5 = open_day_4 + 24 hours;
    uint256 private close_day_5 = open_day_5 + 9 hours;
    // exp
    uint256 exp = 10**18;
    // check per day_mint
    mapping( address => uint256 ) check;

    // eventi
    event Mint( address indexed tokenAddress, address indexed from, uint256 tokenAmount, uint256 paycoinAmount );
    event Burn( address indexed tokenAddress, address indexed from, uint256 tokenAmount, uint256 paycoinAmount );
    event Buy( address indexed tokenAddress, address indexed from, uint256 tokenAmount, uint256 paycoinAmount );
    event Sell( address indexed tokenAddress, address indexed from, uint256 tokenAmount, uint256 paycoinAmount );
    event Swap( address indexed tokenAddressIn, address indexed tokenAddressOut, address indexed from, uint256 tokenAmountIn, uint256 tokenAmountOut, uint256 paycoinAmount );
    event Day_Mint( address indexed tokenAddress, uint256 tokenAmount );

    constructor( address _owner, address _paycoin ) public {
        owner = _owner;
        paycoin = IToken(_paycoin);
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "You are not the marketplace owner!");
        _;
    }

    modifier Open(){
        /*require((block.timestamp > open_day_1 && block.timestamp < close_day_1) ||
                (block.timestamp > open_day_2 && block.timestamp < close_day_2) ||
                (block.timestamp > open_day_3 && block.timestamp < close_day_3) ||
                (block.timestamp > open_day_4 && block.timestamp < close_day_4) ||
                (block.timestamp > open_day_5 && block.timestamp < close_day_5)," Marketplace is closed!");*/
                _;
    }
    

    function addToken( address tokenAddress, uint256 initialAmount ) external onlyOwner {
        require( k[tokenAddress] == 0, "Token has alredy been added!" );
        IToken newToken = IToken(tokenAddress);
        token[tokenAddress] = newToken;
        newToken.minting( address(this), initialAmount );
        newToken.minting( newToken.owner(), initialAmount/20 );
        uint256 initialPaycoins = 10**5 * exp ;
        paycoin.minting( address(this), initialPaycoins );
        paycoin.minting( newToken.owner(), initialPaycoins/2 );
        liquidity[tokenAddress] = initialPaycoins;
        initTokAmount[tokenAddress] = initialAmount;
        price[tokenAddress] = initialPaycoins * exp / initialAmount;
        k[tokenAddress] = initialPaycoins * initialAmount;
    }


    function mint_stake( address tokenAddress, uint256 tokenAmount ) external Open {
        require ( msg.sender == token[tokenAddress].owner(), "You are not the token owner!" );
        uint256 paycoinAmount = tokenAmount * price[tokenAddress] / exp;
        require( token[tokenAddress].balanceOf(address(this)) + tokenAmount <= initTokAmount[tokenAddress] + initTokAmount[tokenAddress]/2, "Minting too many tokens!" );
        token[tokenAddress].transferFrom( tokenAmount, msg.sender, address(this) );
        paycoin.transferFrom( paycoinAmount, msg.sender, address(this) );
        liquidity[tokenAddress] += paycoinAmount;
        k[tokenAddress] = liquidity[tokenAddress] * token[tokenAddress].balanceOf(address(this)) ;
        emit Mint( tokenAddress, msg.sender, tokenAmount, paycoinAmount );
    }

    function burn_stake( address tokenAddress, uint256 tokenAmount ) external Open {
        require ( msg.sender == token[tokenAddress].owner(), "You are not the token owner!" );
        uint256 paycoinAmount = tokenAmount * price[tokenAddress] / exp;
        require( token[tokenAddress].balanceOf(address(this)) - tokenAmount >= initTokAmount[tokenAddress]/2, "Burning too many tokens!" );
        token[tokenAddress].transfer( tokenAmount, msg.sender );
        paycoin.transfer( paycoinAmount, msg.sender );
        liquidity[tokenAddress] -= paycoinAmount;
        k[tokenAddress] = liquidity[tokenAddress] * token[tokenAddress].balanceOf(address(this));
        emit Burn( tokenAddress, msg.sender, tokenAmount, paycoinAmount );
    }


    function paycoinToToken( address tokenAddress, uint256 paycoinAmount ) public view returns (uint256) {
        require( k[tokenAddress] != 0, "Token has not been initialized yet!" );
        return paycoinAmount != 0 ? token[tokenAddress].balanceOf(address(this)) - k[tokenAddress] / (liquidity[tokenAddress] + paycoinAmount) : 0;
    }

    function tokenToPaycoin( address tokenAddress, uint256 tokenAmount ) public view returns (uint256) {
        require( k[tokenAddress] != 0, "Token has not been initialized yet!" ); 
        return tokenAmount != 0 ? liquidity[tokenAddress] - k[tokenAddress] / (token[tokenAddress].balanceOf(address(this)) + tokenAmount) : 0;
    }

    function buy( address tokenAddress, uint256 paycoinAmount ) external Open {
        IToken tokenContract = token[tokenAddress];
        require( msg.sender != tokenContract.owner(), "Owner can't buy his own token!" );

        paycoin.transferFrom( paycoinAmount, msg.sender, address(this) );
        uint256 feeAmount = paycoinAmount*fee/(1000+fee);
        paycoin.transfer( feeAmount, tokenContract.owner() );
        paycoinAmount = paycoinAmount - feeAmount;
        uint256 tokenAmount = paycoinToToken( tokenAddress, paycoinAmount );
        tokenContract.transfer( tokenAmount, msg.sender);
        liquidity[tokenAddress] += paycoinAmount;
        price[tokenAddress] = liquidity[tokenAddress] * exp / tokenContract.balanceOf(address(this));

        emit Buy( tokenAddress, msg.sender, tokenAmount, paycoinAmount );
    }

    function sell( address tokenAddress, uint256 tokenAmount ) external Open {
        IToken tokenContract = token[tokenAddress];
        require( msg.sender != tokenContract.owner(), "Owner can't sell his own token!" );

        uint256 paycoinAmount = tokenToPaycoin( tokenAddress, tokenAmount );
        uint256 feeAmount = paycoinAmount * fee / 1000;

        tokenContract.transferFrom( tokenAmount, msg.sender, address(this) );
        paycoin.transfer( paycoinAmount - feeAmount, msg.sender );
        paycoin.transfer( feeAmount, tokenContract.owner() );

        liquidity[tokenAddress] -= paycoinAmount; 
        price[tokenAddress] = liquidity[tokenAddress] * exp / tokenContract.balanceOf(address(this));

        emit Sell( tokenAddress, msg.sender, tokenAmount, paycoinAmount );
    }

    function swap( address tokenAddressIn, address tokenAddressOut, uint256 tokenAmountIn ) external Open {
        IToken tokenIn = token[tokenAddressIn];
        IToken tokenOut = token[tokenAddressOut];

        uint256 paycoinAmount = tokenToPaycoin( tokenAddressIn, tokenAmountIn );
        uint256 feeAmount = paycoinAmount * fee /1000;
        uint256 tokenAmountOut = paycoinToToken( tokenAddressOut, paycoinAmount );

        paycoin.transferFrom( 2*feeAmount, msg.sender, address(this) );
        paycoin.transfer( feeAmount, tokenIn.owner() );
        paycoin.transfer( feeAmount, tokenOut.owner() );
        tokenIn.transferFrom( tokenAmountIn, msg.sender, address(this) );
        tokenOut.transfer( tokenAmountOut, msg.sender );

        liquidity[tokenAddressIn] -= paycoinAmount;
        liquidity[tokenAddressOut] += paycoinAmount;
        price[tokenAddressIn] = liquidity[tokenAddressIn] * exp / tokenIn.balanceOf(address(this));
        price[tokenAddressOut] = liquidity[tokenAddressOut] * exp / tokenOut.balanceOf(address(this));

        emit Swap( tokenAddressIn, tokenAddressOut, msg.sender, tokenAmountIn, tokenAmountOut, paycoinAmount );
    }


    function day_mint(address tokenAddress) external{
        require( msg.sender == token[tokenAddress].owner(), "You are not the token owner!" );
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
        require(check[tokenAddress] <= day);
        uint256 paycoinAmount = liquidity[tokenAddress];
        paycoin.minting( msg.sender, day * paycoinAmount / 10 );
        check[tokenAddress] = day + 1; 

        emit Day_Mint( tokenAddress, day * paycoinAmount / 10 );
    }

}