import React, { Fragment, useState, useEffect } from 'react';
import socketIOClient from 'socket.io-client';
import './App.css';
import VideoFeed from './Components/VideoFeed/VideoFeed';
import SearchBar from './Components/SearchBar/SearchBar';
import LastArrivalList from './Components/LastArrivalList/LastArrivalList';
import AdminBlock from './Components/AdminBlock/AdminBlock';
import styled from 'styled-components';

function App() {
	// * ---------- STYLE ---------- *
	const TitleOne = styled.h1`
		margin-top: 30px;
		font-size: 50px;
		line-height: 1;
		font-weight: bold;
		color: #013087;
		text-align: center;
	`;
	const MainContainer = styled.main`
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
	`;

	const [response, setResponse] = useState(false);
	const socket = socketIOClient('http://localhost:8080');
	useEffect(() => {
		console.log('Verga');
		//socket.emit('message', 'Hello World!');
	}, []);
	return (
		<Fragment>
			<TitleOne>Late Checker</TitleOne>
			<MainContainer>
				<VideoFeed />
				<SearchBar />
				<LastArrivalList />
				<AdminBlock />
			</MainContainer>
		</Fragment>
	);
}

export default App;
