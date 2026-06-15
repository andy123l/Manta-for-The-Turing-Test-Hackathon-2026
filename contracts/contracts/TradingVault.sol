// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title TradingVault
 * @notice Secure vault for holding trading capital and executing strategies
 * @dev Implements ReentrancyGuard for security
 */
contract TradingVault is ReentrancyGuard, Ownable {
    using SafeERC20 for IERC20;

    // State variables
    IERC20 public token;
    address public trustedExecutor;
    uint256 public totalDeposits;
    uint256 public totalTrades;
    bool public paused;

    // User deposits
    mapping(address => uint256) public deposits;

    // Trade history
    struct Trade {
        uint256 id;
        address user;
        uint256 amount;
        uint256 entryPrice;
        uint256 exitPrice;
        bool success;
        uint256 timestamp;
    }

    Trade[] public trades;

    // Events
    event Deposit(address indexed user, uint256 amount, uint256 timestamp);
    event Withdraw(address indexed user, uint256 amount, uint256 timestamp);
    event TradeExecuted(
        uint256 indexed tradeId,
        address indexed user,
        uint256 amount,
        uint256 entryPrice,
        uint256 exitPrice,
        bool success
    );
    event ExecutorUpdated(address indexed oldExecutor, address indexed newExecutor);
    event PauseStateChanged(bool paused);

    // Modifiers
    modifier onlyExecutor() {
        require(msg.sender == trustedExecutor, "Not authorized executor");
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "Contract is paused");
        _;
    }

    /**
     * @notice Initialize the vault
     * @param _token Address of the ERC20 token (USDT, USDC, etc.)
     */
    constructor(address _token) Ownable(msg.sender) {
        require(_token != address(0), "Invalid token address");
        token = IERC20(_token);
        trustedExecutor = msg.sender;
    }

    /**
     * @notice Deposit tokens into the vault
     * @param amount Amount of tokens to deposit
     */
    function deposit(uint256 amount) external nonReentrant whenNotPaused {
        require(amount > 0, "Amount must be greater than 0");

        token.safeTransferFrom(msg.sender, address(this), amount);
        deposits[msg.sender] += amount;
        totalDeposits += amount;

        emit Deposit(msg.sender, amount, block.timestamp);
    }

    /**
     * @notice Withdraw tokens from the vault
     * @param amount Amount of tokens to withdraw
     */
    function withdraw(uint256 amount) external nonReentrant whenNotPaused {
        require(amount > 0, "Amount must be greater than 0");
        require(deposits[msg.sender] >= amount, "Insufficient balance");

        deposits[msg.sender] -= amount;
        totalDeposits -= amount;

        token.safeTransfer(msg.sender, amount);

        emit Withdraw(msg.sender, amount, block.timestamp);
    }

    /**
     * @notice Execute a trade through the vault
     * @param target Target contract to interact with
     * @param data Encoded function call data
     * @param value ETH value to send (if any)
     * @return success Whether the trade was successful
     */
    function executeTrade(
        address target,
        bytes calldata data,
        uint256 value
    ) external onlyExecutor nonReentrant whenNotPaused returns (bool success) {
        require(target != address(0), "Invalid target address");

        uint256 balanceBefore = token.balanceOf(address(this));

        // Execute the trade
        (success, ) = target.call{value: value}(data);

        uint256 balanceAfter = token.balanceOf(address(this));

        // Record the trade
        totalTrades++;
        trades.push(Trade({
            id: totalTrades,
            user: msg.sender,
            amount: balanceBefore - balanceAfter,
            entryPrice: 0, // Will be updated off-chain
            exitPrice: 0,
            success: success,
            timestamp: block.timestamp
        }));

        emit TradeExecuted(
            totalTrades,
            msg.sender,
            balanceBefore - balanceAfter,
            0,
            0,
            success
        );

        return success;
    }

    /**
     * @notice Update the trusted executor
     * @param newExecutor Address of the new executor
     */
    function setExecutor(address newExecutor) external onlyOwner {
        require(newExecutor != address(0), "Invalid executor address");

        address oldExecutor = trustedExecutor;
        trustedExecutor = newExecutor;

        emit ExecutorUpdated(oldExecutor, newExecutor);
    }

    /**
     * @notice Pause or unpause the contract
     * @param _paused New pause state
     */
    function setPaused(bool _paused) external onlyOwner {
        paused = _paused;
        emit PauseStateChanged(_paused);
    }

    /**
     * @notice Get user's deposit balance
     * @param user Address of the user
     * @return Balance of the user
     */
    function getBalance(address user) external view returns (uint256) {
        return deposits[user];
    }

    /**
     * @notice Get total trades executed
     * @return Total number of trades
     */
    function getTradeCount() external view returns (uint256) {
        return trades.length;
    }

    /**
     * @notice Get trade details by ID
     * @param tradeId ID of the trade
     * @return Trade details
     */
    function getTrade(uint256 tradeId) external view returns (Trade memory) {
        require(tradeId > 0 && tradeId <= trades.length, "Invalid trade ID");
        return trades[tradeId - 1];
    }

    /**
     * @notice Emergency withdrawal (owner only)
     * @param to Recipient address
     * @param amount Amount to withdraw
     */
    function emergencyWithdraw(address to, uint256 amount) external onlyOwner {
        require(to != address(0), "Invalid recipient");
        token.safeTransfer(to, amount);
    }
}
