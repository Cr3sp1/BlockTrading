pragma solidity^0.5.17;

interface IChallenge{
    function one_vs_one(address _rival) external;

    function one_vs_two(address _rival_1, address _rival_2) external;

    function win_one() external;

    function win_two() external;
}