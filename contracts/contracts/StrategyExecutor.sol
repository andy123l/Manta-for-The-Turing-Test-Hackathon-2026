// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title StrategyExecutor
 * @notice Executes trading strategies on-chain
 * @dev Manages multiple strategies with risk controls
 */
contract StrategyExecutor is Ownable, ReentrancyGuard {

    // Strategy structure
    struct Strategy {
        uint256 id;
        string name;
        address target;
        bytes encodedFunction;
        uint256 riskLevel;  // 1-5 (1=low, 5=high)
        bool active;
        uint256 maxPosition;
        uint256 currentPosition;
        uint256 totalExecutions;
        uint256 lastExecution;
    }

    // State variables
    mapping(uint256 => Strategy) public strategies;
    uint256 public strategyCount;
    uint256 public maxRiskLevel;
    uint256 public maxTotalExposure;

    // Events
    event StrategyCreated(
        uint256 indexed strategyId,
        string name,
        address target,
        uint256 riskLevel
    );
    event StrategyUpdated(uint256 indexed strategyId, bool active);
    event StrategyExecuted(
        uint256 indexed strategyId,
        address indexed user,
        uint256 amount,
        bool success
    );
    event RiskParametersUpdated(uint256 maxRisk, uint256 maxExposure);

    // Modifiers
    modifier validStrategy(uint256 strategyId) {
        require(strategyId > 0 && strategyId <= strategyCount, "Invalid strategy");
        require(strategies[strategyId].active, "Strategy not active");
        _;
    }

    constructor() Ownable(msg.sender) {
        maxRiskLevel = 3;  // Default max risk level
        maxTotalExposure = 1000000 * 1e6;  // 1M USDC (6 decimals)
    }

    /**
     * @notice Create a new trading strategy
     * @param name Strategy name
     * @param target Target contract address
     * @param encodedFunction Encoded function to call
     * @param riskLevel Risk level (1-5)
     * @param maxPosition Maximum position size
     * @return strategyId ID of the created strategy
     */
    function createStrategy(
        string calldata name,
        address target,
        bytes calldata encodedFunction,
        uint256 riskLevel,
        uint256 maxPosition
    ) external onlyOwner returns (uint256) {
        require(target != address(0), "Invalid target");
        require(riskLevel >= 1 && riskLevel <= 5, "Invalid risk level");
        require(maxPosition > 0, "Invalid max position");

        strategyCount++;

        strategies[strategyCount] = Strategy({
            id: strategyCount,
            name: name,
            target: target,
            encodedFunction: encodedFunction,
            riskLevel: riskLevel,
            active: true,
            maxPosition: maxPosition,
            currentPosition: 0,
            totalExecutions: 0,
            lastExecution: 0
        });

        emit StrategyCreated(strategyCount, name, target, riskLevel);

        return strategyCount;
    }

    /**
     * @notice Update strategy status
     * @param strategyId Strategy ID
     * @param active New active status
     */
    function updateStrategy(uint256 strategyId, bool active) external onlyOwner {
        require(strategyId > 0 && strategyId <= strategyCount, "Invalid strategy");

        strategies[strategyId].active = active;

        emit StrategyUpdated(strategyId, active);
    }

    /**
     * @notice Execute a trading strategy
     * @param strategyId Strategy to execute
     * @param amount Amount to trade
     * @return success Whether execution was successful
     */
    function executeStrategy(
        uint256 strategyId,
        uint256 amount
    ) external nonReentrant validStrategy(strategyId) returns (bool) {
        Strategy storage strategy = strategies[strategyId];

        // Risk checks
        require(
            strategy.currentPosition + amount <= strategy.maxPosition,
            "Exceeds strategy max position"
        );

        // Execute the strategy
        (bool success, ) = strategy.target.call(
            abi.encodePacked(strategy.encodedFunction, amount)
        );

        // Update strategy state
        if (success) {
            strategy.currentPosition += amount;
            strategy.totalExecutions++;
            strategy.lastExecution = block.timestamp;
        }

        emit StrategyExecuted(strategyId, msg.sender, amount, success);

        return success;
    }

    /**
     * @notice Update risk parameters
     * @param newMaxRisk New maximum risk level
     * @param newMaxExposure New maximum total exposure
     */
    function updateRiskParameters(
        uint256 newMaxRisk,
        uint256 newMaxExposure
    ) external onlyOwner {
        require(newMaxRisk >= 1 && newMaxRisk <= 5, "Invalid risk level");

        maxRiskLevel = newMaxRisk;
        maxTotalExposure = newMaxExposure;

        emit RiskParametersUpdated(newMaxRisk, newMaxExposure);
    }

    /**
     * @notice Get strategy details
     * @param strategyId Strategy ID
     * @return Strategy details
     */
    function getStrategy(uint256 strategyId) external view returns (Strategy memory) {
        require(strategyId > 0 && strategyId <= strategyCount, "Invalid strategy");
        return strategies[strategyId];
    }

    /**
     * @notice Get all active strategies
     * @return Array of active strategy IDs
     */
    function getActiveStrategies() external view returns (uint256[] memory) {
        uint256[] memory activeStrategies = new uint256[](strategyCount);
        uint256 count = 0;

        for (uint256 i = 1; i <= strategyCount; i++) {
            if (strategies[i].active) {
                activeStrategies[count] = i;
                count++;
            }
        }

        // Trim array
        uint256[] memory result = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = activeStrategies[i];
        }

        return result;
    }
}
