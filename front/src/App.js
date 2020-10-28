import React, {useEffect} from "react";
import LoginButton from "./Login";
import LogoutButton from "./Logout";
import {useAuth0} from "@auth0/auth0-react";
import Profile from "./Profile";

function App() {
  const {isAuthenticated} = useAuth0();

  useEffect(() => {
    console.log(isAuthenticated);
  }, [isAuthenticated])

  return (
    <div className="App">
      <h1>Hello</h1>
      <LoginButton/>
      <LogoutButton/>
      <Profile/>
    </div>
  );
}

export default App;
