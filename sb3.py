"""Run the robotron environment using Stable Baselines 3 """

from robotron import RobotronEnv
from wandb.integration.sb3 import WandbCallback
import wandb
from stable_baselines3.common.vec_env import DummyVecEnv, VecFrameStack
from stable_baselines3 import PPO
from gym.wrappers import GrayScaleObservation


def main():
    config = {
        "policy_type": "MlpPolicy",
        "total_timesteps": 5_500_000,
        "lr": 0.000001,
        "env_name": "robotron",
    }

    run = wandb.init(
        project="robotron",
        config=config,
        sync_tensorboard=True,  # auto-upload sb3's tensorboard metrics
        monitor_gym=True,  # auto-upload the videos of agents playing the game
        save_code=True,  # optional
    )

    env = RobotronEnv()
    env = GrayScaleObservation(env, keep_dim=True)
    env = DummyVecEnv([lambda: env])
    env = VecFrameStack(env, 4, channels_order='last')

    model = PPO(config["policy_type"], env, verbose=1, tensorboard_log=f"runs/{run.id}", learning_rate=config["lr"])
    model.learn(
        total_timesteps=config["total_timesteps"],
        callback=WandbCallback(
            gradient_save_freq=100,
            model_save_path=f"models/{run.id}",
            verbose=2,
        ),
    )
    run.finish()


if __name__ == "__main__":
    main()
