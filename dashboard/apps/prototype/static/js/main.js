import $ from 'jquery';
import select2 from 'select2';
import Cookies from 'js-cookie';
import { getProjectData, plotProject } from './project';
import { getServiceData, getServiceFinancials } from './service';
import { createHistory } from 'history';

require('select2/dist/css/select2.min.css');
require('../styles/gov-uk-elements.css');
require('../styles/main.css');


function project(id) {
  // get the DOM element for the graph
  const elem = document.getElementById('fig-a');
  // plot the project
  getProjectData(id, Cookies.get('csrftoken'))
    .then(projectData => plotProject(projectData, elem));

  // dropdown project selector
  $('#projects').select2().on("select2:select", (e) => {
    const projectId = e.params.data.id;
    window.location.href = `/projects/${projectId}`;
  });
}


class ProjectSelector {

  constructor($checkboxes, onChange) {
    this.$checkboxes = $checkboxes;
    this.$checkboxes.change(() => onChange(this.projectIds));
  }

  get projectIds() {
    const ids = this.$checkboxes.get()
      .map(box => box.checked ? box.id : null)
      .filter(Boolean);
    return ids;
  }
}


class ServiceGraph {

  constructor(id, divId) {
    this.id = id;
    this.div = document.getElementById(divId);
    this.props = {};
    this.onInit();
  }

  onInit() {
    getServiceData(this.id, Cookies.get('csrftoken'))
      .then(serviceData => {
        this.props = serviceData;
        this.plot();
      });
  }

  plot(projectIds) {
    if (this.div === null)
      return;
    const financial = getServiceFinancials(this.props, projectIds);
    const name = this.props.name;
    plotProject({financial, name}, this.div);
  }
}


function service(id) {
  // get the DOM element for the graph
  const serviceGraph = new ServiceGraph(id, 'fig-a');
  const $checkboxes = $('ul#projects  li input');
  const projectSelector = new ProjectSelector(
    $checkboxes, projectIds => serviceGraph.plot(projectIds));

  // dropdown service selector
  $('#services').select2().on("select2:select", (e) => {
    const serviceId = e.params.data.id;
    window.location.href = `/services/${serviceId}`;
  });
}


function route(path) {
  // call different loading functions based on page url
  const pattern = /(projects|services)\/(\d+)/;
  const matches = pattern.exec(path);

  if (matches === null)
    return;

  const [_, endpoint, id] = matches;

  switch (endpoint) {
    case 'projects':
      project(id);
      break;
    case 'services':
      service(id);
      break;
  };
}


const location = createHistory().getCurrentLocation();
route(location.pathname);
