import { describe, expect, it } from "@jest/globals";
import { ProcessConfig, STACK_NAME_KEY } from "../src/ts/config";
import { FeatureName } from "../src/ts/types";

describe("config", () => {
  const getActual = (
    config: ProcessConfig,
  ): Record<keyof typeof FeatureName, boolean> => {
    return {
      makeRepoPublicOnApproval: config.isFeatureEnabled(
        FeatureName.makeRepoPublicOnApproval,
      ),
    };
  };
  it("sets defaults", () => {
    const config = ProcessConfig.fromEnv({});
    expect(config.stackName).toBe(undefined);
    const expected: Record<keyof typeof FeatureName, boolean> = {
      makeRepoPublicOnApproval: false,
    };
    const actual = getActual(config);
    expect(actual).toStrictEqual(expected);
  });
  it("has expected values for prod", () => {
    const config = ProcessConfig.fromEnv({ [STACK_NAME_KEY]: "test_prod" });
    expect(config.stackName).toBe("test_prod");
    const expected: Record<keyof typeof FeatureName, boolean> = {
      makeRepoPublicOnApproval: true,
    };
    const actual = getActual(config);
    expect(actual).toStrictEqual(expected);
  });
});
