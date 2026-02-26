import mssql from 'mssql';

const connectionPools = new Map<string, mssql.ConnectionPool>();

export async function getSqlServerConnection(config: {
  id: string;
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
}) {
  const poolKey = `${config.id}_${config.host}_${config.database}`;

  if (connectionPools.has(poolKey)) {
    const pool = connectionPools.get(poolKey)!;
    if (pool.connected) return pool;
    if (pool.connecting) {
      await new Promise((resolve) => pool.once('connect', resolve));
      return pool;
    }
  }

  const sqlConfig: mssql.config = {
    user: config.username,
    password: config.password,
    database: config.database,
    server: config.host,
    port: config.port,
    pool: {
      max: 10,
      min: 0,
      idleTimeoutMillis: 30000
    },
    options: {
      encrypt: true, // For Azure/Neon etc.
      trustServerCertificate: true // For local/self-signed certs
    }
  };

  const pool = new mssql.ConnectionPool(sqlConfig);
  const connectedPool = await pool.connect();
  connectionPools.set(poolKey, connectedPool);

  return connectedPool;
}

export async function executeQuery(pool: mssql.ConnectionPool, query: string, params: Record<string, unknown> = {}) {
  const request = pool.request();
  
  for (const [key, value] of Object.entries(params)) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    request.input(key, value as any); // mssql input expects any
  }

  const result = await request.query(query);
  return result.recordset;
}
