import gymnasium as gym


gym.register(
    id="LeIsaac-Franka-BowlCubeZone-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.bowl_cube_zone_env_cfg:FrankaBowlCubeZoneEnvCfg",
    },
)
