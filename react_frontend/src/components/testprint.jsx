import React, { useRef } from "react";
import { useReactToPrint } from "react-to-print";

const TestPrint = () => {
  const ref = useRef();

  const handlePrint = useReactToPrint({
    content: () => ref.current
  });

  return (
    <div>
      <button onClick={handlePrint}>Print</button>
      <div ref={ref}>
        <h1>Hello World</h1>
        <p>This should print.</p>
      </div>
    </div>
  );
};

export default TestPrint;
