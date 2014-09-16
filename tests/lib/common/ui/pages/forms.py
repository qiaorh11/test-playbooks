import time
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from common.ui.pages import Base, BaseRegion
from common.ui.pages.regions.buttons import Base_Button
from common.ui.pages.regions.lists import List_Region


def input_getter_by_name(locator):
    '''
    Generic property fget method
    '''
    def get_field(self):
        assert hasattr(self, '_locators'), "No self._locators dictionary defined"
        assert locator in self._locators, "No such locator found '{}".format(locator)
        el = self.find_element(*self._locators.get(locator))
        el_type = el.get_attribute('type')
        if el_type in (u'text', u'password', u'email'):
            return el.get_attribute('value')
        elif el_type == u'checkbox':
            return el.is_selected()
        elif el_type == u'select-one':
            select = Select(el)
            if select.all_selected_options:
                return select.all_selected_options[0].get_attribute('value')
            else:
                return None
        elif el_type == u'radio':
            parent_root = el.find_element(*(By.XPATH, '../../..'))
            radio = Radio(self.testsetup, _root_element=parent_root, _item_locator=self._locators.get(locator))
            return radio.value
        else:
            raise NotImplementedError("Unhandled input type: %s" % el_type)
    return get_field


def input_setter_by_name(locator):
    '''
    Generic property fset method
    '''
    def set_field(self, value):
        assert hasattr(self, '_locators'), "No self._locators dictionary defined"
        assert locator in self._locators, "No such locator found '{}".format(locator)
        el = self.find_element(*self._locators.get(locator))
        el_type = el.get_attribute('type')
        if el_type in (u'text', u'password', u'email'):
            el.clear()
            el.send_keys(value)
        elif el_type == u'checkbox':
            assert isinstance(value, (int, bool)), "Checkboxes only accept boolean values"
            if el.is_selected() and not value:
                el.click()
            elif value and not el.is_selected():
                el.click()
        elif el_type == u'select-one':
            select = Select(el)
            select.select_by_value(value)
            self.wait_for_spinny()
        elif el_type == u'radio':
            # The following XPATH is ugly, but chooses the
            # great-great-grandfather of the current locator.  The hope is that
            # other radio options will be a descendant of the
            # great-great-grandfather element.
            parent_root = el.find_element(*(By.XPATH, '../../../..'))
            radio = Radio(self.testsetup, _root_element=parent_root, _item_locator=self._locators.get(locator))
            radio.get(value).click()
        else:
            raise NotImplementedError("Unhandled input type: %s" % el_type)
    return set_field


def input_getter(locator):
    '''
    Generic property fget method
    '''
    def get_field(self):
        el = self.find_element(*locator)
        el_type = el.get_attribute('type')
        if el_type in (u'text', u'password'):
            return self.find_element(*locator).get_attribute('value')
        elif el_type == u'checkbox':
            return self.find_element(*locator).is_selected()
    return get_field


def input_setter(locator):
    '''
    Generic property fset method
    '''
    def set_field(self, value):
        el = self.find_element(*locator)
        el_type = el.get_attribute('type')
        if el_type in (u'text', u'password'):
            el.clear()
            el.send_keys(value)
        elif el_type == u'checkbox':
            el.click()
    return set_field


class Form_Page(Base):
    '''Object that defines various helpers for interacting with browser <form>s'''

    # Sub-classes should define the following title attributes
    _tab_title = "FIXME"
    _breadcrumb_title = "FIXME"

    # Sub-classes should define related objects in the following dictionary
    _related = {}

    # Sub-classes should define locators in the following dictionary
    _locators = {}

    # name = property(base.input_getter(_locators['name']), base.input_setter(_locators['name']))
    # description = property(base.input_getter(_locators['description']), base.input_setter(_locators['description']))

    def click_save(self):
        raise NotImplementedError("Must be implemented by a sub-class")

    def click_reset(self):
        raise NotImplementedError("Must be implemented by a sub-class")

    def fill_field_element_with_wait(self, data, field_element):
        field_element = self.fill_field_element(data, field_element)
        # Stupid wait for ajax interval
        time.sleep(2)
        return field_element

    def fill_field_element_clears_text(self, data, field_element):
        '''Fill field with workaround for javascript clearing behavior'''
        field_element.click()
        time.sleep(1)
        field_element.clear()
        field_element.send_keys(data)

    def fill_field_element(self, data, field_element):
        field_element.clear()
        field_element.send_keys(data)
        return field_element

    def fill_field_by_locator(self, data, *locator):
        field_element = self._selenium_root.find_element(*locator)
        self.fill_field_element(data, field_element)
        return field_element

    def fill_field_by_locator_with_wait(self, data, *locator):
        field_element = self._selenium_root.find_element(*locator)
        self.fill_field_element_with_wait(data, field_element)
        return field_element

    def select_dropdown(self, value, *element):
        select = Select(self._selenium_root.find_element(*element))
        select.select_by_visible_text(value)

    def select_dropdown_by_value(self, value, *element):
        select = Select(self._selenium_root.find_element(*element))
        select.select_by_value(value)

    @property
    def save_btn(self):
        return Base_Button(self.testsetup, _root_element=self.find_element(*self._locators['save_btn']), _item_class=self.get_related('save'))

    @property
    def reset_btn(self):
        return Base_Button(self.testsetup, _root_element=self.find_element(*self._locators['reset_btn']))


class Radio(List_Region):
    '''Describes a radio button group'''
    _item_locator = (By.CSS_SELECTOR, "input[type='radio' and name='{}']")
    _unique_attribute = 'value'

    def selected(self):
        '''Return the selenium element of the currently selected radio option'''
        for el in self.items():
            if el.is_selected():
                return el
        return None

    @property
    def value(self):
        '''Return the value of the currently selected item'''
        selected = self.selected()
        if selected is None:
            return None
        else:
            return selected.get_attribute(self._unique_attribute)
