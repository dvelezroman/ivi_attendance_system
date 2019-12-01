import React, { useState, useEffect } from 'react';
import socketIOClient from 'socket.io-client';
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

	const [response, setResponse] = useState(false);
	const socket = socketIOClient('http://127.0.0.1:5000');
	useEffect(() => {
		//socket.emit('message', { data: 'Hello World!' });
		socket.on('response', response => {
			console.log(response);
		});
	}, []);

	return (
		<>
			{/* <Webcam
				audio={false}
				height={300}
				ref={webcamRef}
				screenshotFormat='image/jpeg'
				width={500}
				videoConstraints={videoConstraints}
			/> */}
			{/* <button onClick={capture}>Capture photo</button> */}
		</>
	);
};

export default WebCamComponent;
