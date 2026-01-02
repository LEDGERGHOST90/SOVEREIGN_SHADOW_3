import logging
from typing import Dict, List, Any, Tuple, Optional
import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces

logger = logging.getLogger(__name__)

class DepthOrderBookRLEnv(gym.Env):
    """
    DEPTH: Order Book RL Scaffold - OpenAI Gym Environment
    A basic OpenAI Gym-compatible environment for simulating order book interactions
    and developing reinforcement learning agents for optimal trade execution.

    The environment simplifies a real order book to a fixed number of price levels
    and simulates price movements based on agent actions and market dynamics.
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self, config: Dict = None):
        super().__init__()
        self.config = config or {}
        self.num_levels = self.config.get("num_levels", 5) # Number of price levels on each side of the order book
        self.initial_price = self.config.get("initial_price", 100.0)
        self.price_tick_size = self.config.get("price_tick_size", 0.01)
        self.initial_cash = self.config.get("initial_cash", 10000.0)
        self.initial_asset_holdings = self.config.get("initial_asset_holdings", 0.0)
        self.max_order_size = self.config.get("max_order_size", 10.0) # Max quantity per order
        self.max_steps = self.config.get("max_steps", 100)

        self.current_step = 0
        self.current_cash = self.initial_cash
        self.current_asset_holdings = self.initial_asset_holdings
        self.current_mid_price = self.initial_price
        self.order_book: Dict[str, List[Tuple[float, float]]] = self._initialize_order_book() # { 'bids': [(price, qty)], 'asks': [...] }

        # Define action and observation spaces
        # Action: (action_type, price_level_offset, quantity_fraction)
        # action_type: 0=HOLD, 1=BUY (limit), 2=SELL (limit)
        # price_level_offset: integer from -num_levels to num_levels (relative to mid-price)
        # quantity_fraction: float from 0 to 1 (fraction of max_order_size)
        self.action_space = spaces.Dict({
            "action_type": spaces.Discrete(3), # HOLD, BUY, SELL
            "price_level_offset": spaces.Discrete(2 * self.num_levels + 1, start=-self.num_levels), 
            "quantity_fraction": spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)
        })

        # Observation: (mid_price, bid_prices, bid_quantities, ask_prices, ask_quantities, cash, asset_holdings)
        self.observation_space = spaces.Dict({
            "mid_price": spaces.Box(low=0, high=np.inf, shape=(1,), dtype=np.float32),
            "bids": spaces.Box(low=0, high=np.inf, shape=(self.num_levels * 2,), dtype=np.float32), # prices, quantities interleaved
            "asks": spaces.Box(low=0, high=np.inf, shape=(self.num_levels * 2,), dtype=np.float32), # prices, quantities interleaved
            "cash": spaces.Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float32),
            "asset_holdings": spaces.Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float32),
        })

        logger.info("DEPTH Order Book RL Environment initialized.")

    def _initialize_order_book(self) -> Dict[str, List[Tuple[float, float]]]:
        """
        Creates a synthetic order book around the initial price.
        """
        bids = []
        asks = []
        for i in range(1, self.num_levels + 1):
            bid_price = self.initial_price - i * self.price_tick_size
            ask_price = self.initial_price + i * self.price_tick_size
            # Random quantities for simplicity
            bids.append((bid_price, np.random.uniform(1, 10)))
            asks.append((ask_price, np.random.uniform(1, 10)))
        return {"bids": sorted(bids, key=lambda x: x[0], reverse=True), 
                "asks": sorted(asks, key=lambda x: x[0])}

    def _get_observation(self) -> Dict[str, np.ndarray]:
        """
        Returns the current observation of the environment.
        """
        obs_bids = []
        for price, qty in self.order_book["bids"]:
            obs_bids.extend([price, qty])
        obs_asks = []
        for price, qty in self.order_book["asks"]:
            obs_asks.extend([price, qty])

        return {
            "mid_price": np.array([self.current_mid_price], dtype=np.float32),
            "bids": np.array(obs_bids, dtype=np.float32),
            "asks": np.array(obs_asks, dtype=np.float32),
            "cash": np.array([self.current_cash], dtype=np.float32),
            "asset_holdings": np.array([self.current_asset_holdings], dtype=np.float32),
        }

    def _take_action(self, action: Dict[str, Any]) -> Tuple[float, float]:
        """
        Processes the agent's action and modifies the order book/portfolio.
        Returns (executed_price, executed_quantity)
        """
        action_type = action["action_type"]
        price_offset = action["price_level_offset"]
        quantity_fraction = action["quantity_fraction"][0] # Extract scalar from Box
        quantity = quantity_fraction * self.max_order_size

        executed_price = 0.0
        executed_quantity = 0.0
        reward = 0.0

        if action_type == 1: # BUY
            target_price = self.current_mid_price + price_offset * self.price_tick_size
            # Simulate market order for simplicity: buy at best ask if available and price is competitive
            if self.order_book["asks"] and target_price >= self.order_book["asks"][0][0]:
                best_ask_price, best_ask_qty = self.order_book["asks"][0]
                filled_qty = min(quantity, best_ask_qty)
                cost = filled_qty * best_ask_price

                if self.current_cash >= cost:
                    self.current_cash -= cost
                    self.current_asset_holdings += filled_qty
                    executed_price = best_ask_price
                    executed_quantity = filled_qty
                    self.order_book["asks"][0] = (best_ask_price, best_ask_qty - filled_qty)
                    if self.order_book["asks"][0][1] <= 0: # Remove if fully filled
                        self.order_book["asks"].pop(0)
                    reward = filled_qty * (self.initial_price - best_ask_price) # Simple reward: buy low
                else:
                    reward = -1 # Penalty for failing to execute due to lack of cash
            else:
                reward = -0.1 # Small penalty for not executing

        elif action_type == 2: # SELL
            target_price = self.current_mid_price + price_offset * self.price_tick_size
            # Simulate market order for simplicity: sell at best bid if available and price is competitive
            if self.order_book["bids"] and target_price <= self.order_book["bids"][0][0]:
                best_bid_price, best_bid_qty = self.order_book["bids"][0]
                filled_qty = min(quantity, best_bid_qty)

                if self.current_asset_holdings >= filled_qty:
                    self.current_cash += filled_qty * best_bid_price
                    self.current_asset_holdings -= filled_qty
                    executed_price = best_bid_price
                    executed_quantity = filled_qty
                    self.order_book["bids"][0] = (best_bid_price, best_bid_qty - filled_qty)
                    if self.order_book["bids"][0][1] <= 0: # Remove if fully filled
                        self.order_book["bids"].pop(0)
                    reward = filled_qty * (best_bid_price - self.initial_price) # Simple reward: sell high
                else:
                    reward = -1 # Penalty for failing to execute due to lack of assets
            else:
                reward = -0.1 # Small penalty for not executing

        # Action type 0 is HOLD, no immediate execution, just market movement
        
        return executed_price, executed_quantity, reward

    def _update_market(self):
        """
        Simulates market movement (mid-price fluctuation, order book refresh).
        """
        # Simulate mid-price random walk
        self.current_mid_price += np.random.normal(0, self.price_tick_size * 2)
        self.current_mid_price = max(self.price_tick_size, self.current_mid_price) # Price cannot go below 0
        
        # Regenerate order book around new mid-price (simplified for scaffold)
        self.order_book = self._initialize_order_book()
        # Introduce some randomness to quantities
        for i in range(len(self.order_book["bids"])):
            price, qty = self.order_book["bids"][i]
            self.order_book["bids"][i] = (price, qty * np.random.uniform(0.8, 1.2))
        for i in range(len(self.order_book["asks"])):
            price, qty = self.order_book["asks"][i]
            self.order_book["asks"][i] = (price, qty * np.random.uniform(0.8, 1.2))

    def step(self, action: Dict[str, Any]) -> Tuple[Dict[str, np.ndarray], float, bool, bool, Dict]:
        """
        Takes an action in the environment and returns the next observation,
        reward, terminated, truncated, and info.
        """
        self.current_step += 1

        executed_price, executed_quantity, action_reward = self._take_action(action)
        self._update_market()

        # Calculate portfolio value for end-of-episode reward and info
        portfolio_value = self.current_cash + self.current_asset_holdings * self.current_mid_price
        
        # Simple reward: positive for increasing portfolio value
        # A more sophisticated reward function would consider transaction costs, slippage, etc.
        reward = action_reward + (portfolio_value - (self.initial_cash + self.initial_asset_holdings * self.initial_price)) / self.initial_price / self.max_steps

        terminated = self.current_step >= self.max_steps
        truncated = False # Or implement specific truncation conditions
        info = {"portfolio_value": portfolio_value,
                "executed_price": executed_price,
                "executed_quantity": executed_quantity}

        logger.debug(f"Step {self.current_step}: Action={action['action_type']}, Reward={reward:.4f}, Portfolio Value={portfolio_value:.2f}")

        return self._get_observation(), reward, terminated, truncated, info

    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None) -> Tuple[Dict[str, np.ndarray], Dict]:
        """
        Resets the environment to its initial state.
        """
        super().reset(seed=seed)
        self.current_step = 0
        self.current_cash = self.initial_cash
        self.current_asset_holdings = self.initial_asset_holdings
        self.current_mid_price = self.initial_price
        self.order_book = self._initialize_order_book()
        logger.info("DEPTH Order Book RL Environment reset.")

        info = {"portfolio_value": self.initial_cash + self.initial_asset_holdings * self.initial_price}
        return self._get_observation(), info

    def render(self):
        """
        Renders the environment (for visualization).
        For a text-based environment, this might print the order book state.
        """
        if self.render_mode == "human":
            print(f"\n--- Step {self.current_step} ---")
            print(f"Mid Price: {self.current_mid_price:.2f}")
            print("Order Book Bids (Price, Qty):")
            for price, qty in self.order_book["bids"]:
                print(f"  {price:.2f}: {qty:.2f}")
            print("Order Book Asks (Price, Qty):")
            for price, qty in self.order_book["asks"]:
                print(f"  {price:.2f}: {qty:.2f}")
            print(f"Cash: {self.current_cash:.2f}, Assets: {self.current_asset_holdings:.2f}")
            print(f"Portfolio Value: {self.current_cash + self.current_asset_holdings * self.current_mid_price:.2f}")

    def close(self):
        """
        Cleans up resources.
        """
        logger.info("DEPTH Order Book RL Environment closed.")

# Example usage (for testing and basic agent interaction)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    env = DepthOrderBookRLEnv(config={
        "num_levels": 3,
        "initial_price": 100.0,
        "price_tick_size": 0.05,
        "max_order_size": 5.0,
        "max_steps": 10
    })

    obs, info = env.reset()
    env.render() # Initial state

    # Simple random agent for demonstration
    for _ in range(env.max_steps):
        action_type = np.random.randint(0, 3) # 0:HOLD, 1:BUY, 2:SELL
        price_offset = np.random.randint(-env.num_levels, env.num_levels + 1)
        quantity_fraction = np.random.rand(1)

        action = {
            "action_type": action_type,
            "price_level_offset": price_offset,
            "quantity_fraction": quantity_fraction
        }

        obs, reward, terminated, truncated, info = env.step(action)
        env.render()

        if terminated or truncated:
            break

    env.close()
    print(f"\nFinal Portfolio Value: {info['portfolio_value']:.2f}")
