// the application routes

'use strict';

// react: https://github.com/facebook/react
import React from 'react';
// react-router: https://github.com/rackt/react-router
import {Route} from 'react-router';
// lodash: https://github.com/lodash/lodash
import _ from 'lodash';
// local imports
import CalendarRoot from './views/calendar/index'
import GradebookRoot from './views/gradebook/index'
import SyllabusRoot from './views/index'

// the potential routes for each role (actual routes are defined in index.js)
let all_routes = [
    {
        name: 'my calendar',
        route: 'calendar',
        path: '/',
        handler: CalendarRoot,
        allowed_roles: ['teacher', 'student'], 
        show_in_nav: true,
        icon: 'calendar',
    },
    {
        name: 'gradebook',
        route: 'gradebook',
        path: '/gradebook',
        handler: GradebookRoot,
        allowed_roles: ['teacher'], 
        show_in_nav: true,
        icon: 'book',
    }
];

// the current user's role (for now)
let roles = ['admin'];

// return the posible navigation items for the current user
function get_routes_for_user(){

    // figure out the routes for the user
    let routes = [];
    // for each potential route
    _.each(all_routes, route => {
        // if the user satisfies the role requirement
        if (_.intersection(route.allowed_roles, roles).length 
            || _.contains(roles, 'admin') ){
            // add the route to the list
            routes.push(route);
        }
    });

    // return the list of routes
    return routes;
}

// export the route elements for the current user
// export let route_elements = (
//     <Route handler={SyllabusRoot}>
//         { _.map( get_routes_for_user(), function(item) {
//             return <Route name={item.route} path={item.path} handler={item.handler} key={item.name} />
//         })}
//     </Route>
// );
export let route_elements = (
    <Route handler={SyllabusRoot}>
        <Route name="calendar" path="/" handler={CalendarRoot}/>
        <Route name="gradebook" path="/gradebook/?:identifier?" handler={GradebookRoot}/>
    </Route>
)

// export the list of routes
export default get_routes_for_user();

// end of file
