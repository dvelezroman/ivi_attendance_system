import React from 'react';
import Webcam from 'react-webcam';

const videoConstraints = {
	width: 500,
	height: 300,
	facingMode: 'user'
};

const WebCamComponent = () => {
	const webcamRef = React.useRef(null);

	const capture = React.useCallback(() => {
		const imageSrc = webcamRef.current.getScreenshot();
	}, [webcamRef]);

	return (
		<>
			<Webcam
				audio={false}
				height={300}
				ref={webcamRef}
				screenshotFormat='image/jpeg'
				width={500}
				videoConstraints={videoConstraints}
			/>
			{/* <button onClick={capture}>Capture photo</button> */}
		</>
	);
};

export default WebCamComponent;
