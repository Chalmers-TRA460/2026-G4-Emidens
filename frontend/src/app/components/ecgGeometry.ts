export const ECG_NODES: readonly [number, number][] = [
  [5, 18], [11, 18], [14, 11], [17, 22], [21, 14], [27, 14],
];

export const ECG_POINTS = ECG_NODES.map(([x, y]) => `${x},${y}`).join(" ");
