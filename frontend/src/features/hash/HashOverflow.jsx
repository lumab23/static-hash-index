const mockHashData = {
  key: "banana",
  hashValue: 184,
  bucketId: 4,
  bucketCapacity: 3,
  bucketOccupancy: 3,
  collisionCount: 12,
  collisionRate: 2.57,
  overflowBucketCount: 3,
  overflowRate: 6.0,
  overflowEntries: ["banana", "abacaxi"],
};

function HashOverflow() {
  const data = mockHashData;

  return (
    <section>
      <h2>Hash, Colisão e Overflow</h2>

      <div>
        <h3>Cálculo do Hash</h3>

        <p>
          Chave: <strong>{data.key}</strong>
        </p>

        <p>
          Hash: <strong>{data.hashValue}</strong>
        </p>

        <p>
          Bucket escolhido: <strong>{data.bucketId}</strong>
        </p>
      </div>

      <div>
        <h3>Ocupação do Bucket</h3>

        <p>
          {data.bucketOccupancy} / {data.bucketCapacity}
        </p>

        {data.bucketOccupancy >= data.bucketCapacity && (
          <p>Bucket primário cheio</p>
        )}
      </div>

      <div>
        <h3>Colisões</h3>

        <p>Total: {data.collisionCount}</p>
        <p>Taxa: {data.collisionRate}%</p>
      </div>

      <div>
        <h3>Overflow</h3>

        <p>Buckets com overflow: {data.overflowBucketCount}</p>
        <p>Taxa: {data.overflowRate}%</p>

        <ul>
          {data.overflowEntries.map((entry) => (
            <li key={entry}>{entry}</li>
          ))}
        </ul>
      </div>
    </section>
  );
}

export default HashOverflow;