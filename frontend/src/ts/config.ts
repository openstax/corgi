import { FeatureName, Config } from "./types";

interface Env extends Record<string, string | undefined> {}

const PROD_REGEX = /[\s:_-]prod(uction)?$/i;

export class ProcessConfig implements Config {
  private readonly isProd: boolean;
  private readonly featureStates: Record<FeatureName, boolean>;

  constructor(public readonly stackName: string | undefined) {
    this.isProd = stackName !== undefined && PROD_REGEX.test(stackName);
    this.featureStates = {
      [FeatureName.makeRepoPublicOnApproval]: this.isProd,
    };
  }

  isFeatureEnabled(featureName: FeatureName) {
    return this.featureStates[featureName];
  }

  static fromEnv(env: Env) {
    return new ProcessConfig(env.STACK_NAME);
  }
}
