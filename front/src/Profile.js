import React, {useEffect, useState} from "react";
import {useAuth0} from "@auth0/auth0-react";

const Profile = () => {
  const {user, isAuthenticated, getAccessTokenSilently} = useAuth0();
  const [userMetadata, setUserMetadata] = useState(null);
  const [apiData, setApiData] = useState(null);

  useEffect(() => {
    const fetchAPI = async () => {
      const domain = "dev-0gh3h3gj.eu.auth0.com";
      try {
        const accessToken = await getAccessTokenSilently({
          audience: `https://${domain}/api/v2/`,
          scope: "read:current_user",
        });
        await fetch(
          "http://localhost:5000/api/redis-data",
          {
            headers: {
              "Authorization": `Bearer ${accessToken}`,
              "Content-Type": "application/json",
            },
          }
        )
          .then(resp => (resp.json()))
          .then(res => {
            console.log(res)
            setApiData(res);
          })

      } catch (e) {
        console.log(e.message);
      }
    };

    fetchAPI();

  }, [isAuthenticated]);

  return (
    isAuthenticated && (
      <div>
        <img src={user.picture} alt={user.name}/>
        <h2>{user.name}</h2>
        <p>{user.email}</p>
        <h3>User Metadata</h3>
        {apiData !== null
          ? (
            <div>
              <h2>Api data</h2>
              <div>{apiData}</div>
            </div>
          ) : (
            <div>
              <h2>No api data yet</h2>
            </div>
          )
        }
      </div>
    )
  );
};

export default Profile;