"""
Strategy Cloning Service
Allows users to clone and customize existing strategies.
"""

from django.db import transaction
from django.utils import timezone
import copy

from stocks.models import TradingStrategy, StrategyClone, PaperTradingAccount


class StrategyCloning:
    """
    Service for cloning strategies with customization support.
    """

    @staticmethod
    def clone_strategy(original_strategy_id, user, customizations=None, create_paper_account=True):
        """
        Clone a strategy for a user with optional customizations.

        Args:
            original_strategy_id: ID of strategy to clone
            user: User object who is cloning
            customizations: dict of customization options
            create_paper_account: bool - create new paper trading account for clone

        Returns:
            dict: {'success': bool, 'cloned_strategy_id': int, 'message': str}
        """
        try:
            original = TradingStrategy.objects.get(id=original_strategy_id)
        except TradingStrategy.DoesNotExist:
            return {'success': False, 'message': 'Original strategy not found'}

        # Check if strategy is clonable (must be public or unlisted)
        if original.visibility == 'private':
            return {'success': False, 'message': 'Cannot clone private strategy'}

        # Check if user already cloned this strategy
        existing_clone = StrategyClone.objects.filter(
            original_strategy=original,
            user=user
        ).first()

        if existing_clone:
            return {
                'success': False,
                'message': 'You have already cloned this strategy',
                'existing_clone_id': existing_clone.cloned_strategy.id
            }

        # Default customizations
        if customizations is None:
            customizations = {}

        with transaction.atomic():
            # Create cloned strategy
            cloned = TradingStrategy.objects.create(
                user=user,
                name=customizations.get('name', f"{original.name} (Clone)"),
                description=customizations.get('description', original.description),
                strategy_type=original.strategy_type,
                strategy_code=original.strategy_code,
                configuration=copy.deepcopy(original.configuration),
                entry_rules=copy.deepcopy(original.entry_rules),
                exit_rules=copy.deepcopy(original.exit_rules),

                # Apply customized risk management
                max_position_size=customizations.get('max_position_size', original.max_position_size),
                max_portfolio_risk=customizations.get('max_portfolio_risk', original.max_portfolio_risk),
                stop_loss_pct=customizations.get('stop_loss_pct', original.stop_loss_pct),
                take_profit_pct=customizations.get('take_profit_pct', original.take_profit_pct),

                # Clone starts as private draft
                visibility=customizations.get('visibility', 'private'),
                status='draft',
            )

            # Create paper trading account if requested
            if create_paper_account:
                initial_balance = customizations.get('initial_balance', 100000.0)
                paper_account = PaperTradingAccount.objects.create(
                    user=user,
                    account_name=f"{cloned.name} - Paper Account",
                    initial_balance=initial_balance,
                    current_balance=initial_balance,
                    is_active=True
                )
                cloned.paper_account = paper_account
                cloned.status = 'paper_trading'
                cloned.save()

            # Track the clone relationship
            clone_record = StrategyClone.objects.create(
                original_strategy=original,
                cloned_strategy=cloned,
                user=user,
                customizations=customizations,
                is_modified=bool(customizations)
            )

            # Increment clone count on original
            original.clone_count += 1
            original.save()

        return {
            'success': True,
            'cloned_strategy_id': cloned.id,
            'clone_record_id': clone_record.id,
            'message': f'Successfully cloned strategy: {cloned.name}',
            'paper_account_created': create_paper_account
        }

    @staticmethod
    def customize_cloned_strategy(clone_record_id, new_customizations):
        """
        Update customizations on an already cloned strategy.

        Args:
            clone_record_id: StrategyClone ID
            new_customizations: dict of new customization values

        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            clone_record = StrategyClone.objects.get(id=clone_record_id)
        except StrategyClone.DoesNotExist:
            return {'success': False, 'message': 'Clone record not found'}

        cloned_strategy = clone_record.cloned_strategy

        with transaction.atomic():
            # Update cloned strategy with new customizations
            if 'name' in new_customizations:
                cloned_strategy.name = new_customizations['name']

            if 'description' in new_customizations:
                cloned_strategy.description = new_customizations['description']

            if 'max_position_size' in new_customizations:
                cloned_strategy.max_position_size = new_customizations['max_position_size']

            if 'max_portfolio_risk' in new_customizations:
                cloned_strategy.max_portfolio_risk = new_customizations['max_portfolio_risk']

            if 'stop_loss_pct' in new_customizations:
                cloned_strategy.stop_loss_pct = new_customizations['stop_loss_pct']

            if 'take_profit_pct' in new_customizations:
                cloned_strategy.take_profit_pct = new_customizations['take_profit_pct']

            if 'entry_rules' in new_customizations:
                cloned_strategy.entry_rules = new_customizations['entry_rules']

            if 'exit_rules' in new_customizations:
                cloned_strategy.exit_rules = new_customizations['exit_rules']

            if 'configuration' in new_customizations:
                cloned_strategy.configuration.update(new_customizations['configuration'])

            cloned_strategy.save()

            # Update clone record
            clone_record.customizations.update(new_customizations)
            clone_record.is_modified = True
            clone_record.save()

        return {
            'success': True,
            'message': 'Strategy customizations updated',
            'cloned_strategy_id': cloned_strategy.id
        }

    @staticmethod
    def get_clone_lineage(strategy_id):
        """
        Get the clone lineage (original and all clones) for a strategy.

        Returns:
            dict: {'success': bool, 'is_clone': bool, 'original': dict, 'clones': list}
        """
        try:
            strategy = TradingStrategy.objects.get(id=strategy_id)
        except TradingStrategy.DoesNotExist:
            return {'success': False, 'message': 'Strategy not found'}

        # Check if this strategy is a clone
        clone_source = None
        try:
            clone_record = StrategyClone.objects.get(cloned_strategy=strategy)
            clone_source = {
                'id': clone_record.original_strategy.id,
                'name': clone_record.original_strategy.name,
                'user': clone_record.original_strategy.user.email,
                'cloned_at': clone_record.cloned_at,
                'customizations': clone_record.customizations,
                'is_modified': clone_record.is_modified
            }
        except StrategyClone.DoesNotExist:
            pass

        # Get all clones of this strategy
        clones = StrategyClone.objects.filter(original_strategy=strategy).select_related('cloned_strategy', 'user')

        clone_list = [
            {
                'id': clone.cloned_strategy.id,
                'name': clone.cloned_strategy.name,
                'user': clone.user.email,
                'cloned_at': clone.cloned_at,
                'is_modified': clone.is_modified,
                'status': clone.cloned_strategy.status,
                'total_trades': clone.cloned_strategy.total_trades
            }
            for clone in clones
        ]

        return {
            'success': True,
            'strategy_id': strategy.id,
            'strategy_name': strategy.name,
            'is_clone': clone_source is not None,
            'clone_source': clone_source,
            'clones': clone_list,
            'clone_count': len(clone_list)
        }

    @staticmethod
    def get_user_clones(user):
        """
        Get all strategies cloned by a user.

        Returns:
            QuerySet: StrategyClone queryset
        """
        return StrategyClone.objects.filter(user=user).select_related(
            'original_strategy',
            'cloned_strategy'
        ).order_by('-cloned_at')

    @staticmethod
    def compare_clone_performance(clone_record_id):
        """
        Compare performance of cloned strategy vs original.

        Returns:
            dict: Performance comparison data
        """
        try:
            clone_record = StrategyClone.objects.get(id=clone_record_id)
        except StrategyClone.DoesNotExist:
            return {'success': False, 'message': 'Clone record not found'}

        original = clone_record.original_strategy
        cloned = clone_record.cloned_strategy

        # Compare key metrics
        comparison = {
            'success': True,
            'original': {
                'id': original.id,
                'name': original.name,
                'annual_return': float(original.annual_return) if original.annual_return else None,
                'sharpe_ratio': float(original.sharpe_ratio) if original.sharpe_ratio else None,
                'max_drawdown': float(original.max_drawdown) if original.max_drawdown else None,
                'win_rate': float(original.win_rate) if original.win_rate else None,
                'total_trades': original.total_trades
            },
            'cloned': {
                'id': cloned.id,
                'name': cloned.name,
                'annual_return': float(cloned.annual_return) if cloned.annual_return else None,
                'sharpe_ratio': float(cloned.sharpe_ratio) if cloned.sharpe_ratio else None,
                'max_drawdown': float(cloned.max_drawdown) if cloned.max_drawdown else None,
                'win_rate': float(cloned.win_rate) if cloned.win_rate else None,
                'total_trades': cloned.total_trades
            },
            'customizations': clone_record.customizations,
            'is_modified': clone_record.is_modified
        }

        # Calculate deltas
        if original.annual_return and cloned.annual_return:
            comparison['annual_return_delta'] = float(cloned.annual_return) - float(original.annual_return)

        if original.sharpe_ratio and cloned.sharpe_ratio:
            comparison['sharpe_ratio_delta'] = float(cloned.sharpe_ratio) - float(original.sharpe_ratio)

        if original.win_rate and cloned.win_rate:
            comparison['win_rate_delta'] = float(cloned.win_rate) - float(original.win_rate)

        return comparison
