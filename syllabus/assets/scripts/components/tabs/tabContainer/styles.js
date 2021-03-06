// the styles used by the TabContainer component

// lodash: https://github.com/lodash/lodash
import _ from 'lodash';
// tab images
import left_edge_image from './images/left.png';
import right_edge_image from './images/right.png';
import center_image from './images/center.png';
// active tab images
import left_edge_active_image from './images/left_active.png';
import right_edge_active_image from './images/right_active.png';
import center_active_image from './images/center_active.png';

let menu_element_height = '35px';
let menu_element_edge_width = '25px';

export let menu_element_style = {
    display: 'inline',
    height: menu_element_height,
    cursor: 'pointer',
    marginLeft: '-6%',
    lineHeight: menu_element_height,
    zIndex: 1,
    position: 'relative',
    fontSize: '12px',
    color: '#796804',
    whiteSpace: 'nowrap',
    fontFamily: '"HelveticaNeueBlack", "HelveticaNeue-Black", "Helvetica Neue Black", "HelveticaNeue", "Helvetica Neue", "TeXGyreHerosBold", "Arial Black", sans-serif',
    fontWeight:600,
};

// "inherit" from the non active case
export let menu_element_active_style = _.assign({}, menu_element_style, {
    zIndex: 2
});

export let menu_element_left_edge_style = {
    backgroundImage: `url('${left_edge_image}')`,
    width: menu_element_edge_width,
    height: menu_element_height,
    backgroundSize: 'cover',
    display: 'inline-block',
}

// "inherit" from the non active case
export let menu_element_left_edge_active_style = _.assign({}, menu_element_left_edge_style, {
    backgroundImage: `url('${left_edge_active_image}')`,
});

export let menu_element_right_edge_style = {
    backgroundImage: `url('${right_edge_image}')`,
    width: menu_element_edge_width,
    height: menu_element_height,
    backgroundSize: 'cover',
    display: 'inline-block',
}

// "inherit" from the non active case
export let menu_element_right_edge_active_style = _.assign({}, menu_element_right_edge_style, {
    backgroundImage: `url('${right_edge_active_image}')`,
});

export let menu_element_center_style = {
    backgroundImage: `url('${center_image}')`,
    height: menu_element_height,
    display: 'inline-block',
}

// "inherit" from the non active case
export let menu_element_center_active_style = _.assign({}, menu_element_center_style, {
    backgroundImage: `url('${center_active_image}')`,
});

export let list_container_style = {
    padding: '0',
    margin: '0',
    display: 'inline-block',
};

export let menu_toolbar_style = {
    float: 'right',
    display: 'none'
};

export let header_style = {
    padding: '0px 40px 0px 40px',
};

export let container_style = {
    padding: '20px',
    height: '100%',
};

// end of file