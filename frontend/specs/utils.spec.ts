import { expect, describe, it } from "@jest/globals";
import { sortBy } from "../src/ts/utils";

describe("sortBy", () => {
  it("Does lexicographic sorting", () => {
    const testData = [
      [0, 1, 2],
      [2, 1, 3],
      [2, 0, 3],
      [3, 4, 7],
    ];
    const expected = [
      [0, 1, 2],
      [2, 0, 3],
      [2, 1, 3],
      [3, 4, 7],
    ];
    const sorted = sortBy(testData.slice(), [
      { key: 0 },
      { key: 1 },
      { key: 2 },
    ]);
    expect(expected).not.toStrictEqual(testData);
    expect(sorted).toStrictEqual(expected);
  });
  it("Supports reverse sort", () => {
    const testData = [
      [2, 0, 3],
      [0, 1, 2],
      [2, 2, 4],
      [2, 1, 3],
      [3, 4, 7],
      [3, 4, 7],
    ];
    const expected = [
      [3, 4, 7],
      [3, 4, 7],
      [2, 2, 4],
      [2, 1, 3],
      [2, 0, 3],
      [0, 1, 2],
    ];
    // Sort by all columns, first two descending, last ascending
    const sorted = sortBy(testData.slice(), [
      { key: 0, desc: true },
      { key: 1, desc: true },
      { key: 2, desc: false },
    ]);
    expect(expected).not.toStrictEqual(testData);
    expect(sorted).toStrictEqual(expected);
  });
  it("can sort by nested arrays", () => {
    const testData = [
      [[0], [1], [2]],
      [[0], [1], [3]],
      [[3], [4], [4]],
      [[2], [1], [3]],
      [[3], [2], [7]],
      [[3], [4], [7]],
    ];
    const expected = [
      [[0], [1], [3]],
      [[0], [1], [2]],
      [[2], [1], [3]],
      [[3], [4], [7]],
      [[3], [4], [4]],
      [[3], [2], [7]],
    ];
    // Sort by all columns, first two descending, last ascending
    const sorted = sortBy(testData.slice(), [
      { key: 0 },
      { key: 1, desc: true },
      { key: 2, desc: true },
    ]);
    expect(expected).not.toStrictEqual(testData);
    expect(sorted).toStrictEqual(expected);
  });
});
