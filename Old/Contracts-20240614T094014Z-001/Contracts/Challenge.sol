pragma solidity^0.5.17;

import "./IPaycoin.sol";
import "./IChallenge.sol";

contract Challenge is IChallenge{

    address private paycoin;
    uint256 private exp;
    uint256 private start;
    bool private winner_one = false;
    bool private winner_two = false;
    address private challenger;
    address private rival;
    mapping (address => uint256) private single_challenges;
    mapping (address => uint256) private team_challenges;

    event One_vs_One(address indexed _challenger, address indexed _rival);
    event One_vs_Two(address indexed _challenger, address indexed _rival_1, address indexed _rival_2);
    event Win_One(address indexed _winner, uint256 indexed reward);
    event Win_Two(address indexed _winner, uint256 indexed reward);

    constructor (address _paycoin) public{
        paycoin = _paycoin;
        exp = 10 ** IPaycoin(paycoin).decimals();
    }
    function one_vs_one(address _rival) public {
        require(single_challenges[msg.sender] < 10, "Too much challenges");
        single_challenges[msg.sender] += 1;
        IPaycoin(paycoin).mint(msg.sender, 1000 * exp);
        start = block.timestamp;
        winner_one = true;
        challenger = msg.sender;
        rival = _rival;
        emit One_vs_One(msg.sender, _rival);
    }

    function one_vs_two(address _rival_1, address _rival_2) public{
        require(team_challenges[msg.sender] < 10, "Too much challenges");
        team_challenges[msg.sender] += 1;
        IPaycoin(paycoin).mint(msg.sender, 2000 * exp);
        start = block.timestamp;
        winner_two = true;
        emit One_vs_Two(msg.sender, _rival_1, _rival_2);
    }

    function win_one() public{
        require(msg.sender == challenger || msg.sender == rival, "Permission denied");
        require(block.timestamp > start + 20 seconds, "Too Early");
        require(winner_one, "Too Late");
        winner_one = false;
        IPaycoin(paycoin).mint(msg.sender, 10000 * exp);
        emit Win_One(msg.sender, 20000 * exp);
    }

    function win_two() public{
        require(block.timestamp > start + 20 seconds, "Too Early");
        require(winner_two, "Too Late");
        winner_two = false;
        IPaycoin(paycoin).mint(msg.sender, 50000 * exp);
        emit Win_Two(msg.sender, 50000 *exp);
    }
}